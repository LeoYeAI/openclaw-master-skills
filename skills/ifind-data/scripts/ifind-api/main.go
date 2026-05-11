package main

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
	"time"
)

// ─── 编译嵌入的常量 ───
const (
	ifindBillingURL = "https://ifind.skillapp.vip"
	ifindAPISecret  = "ps_123c80aaf4c7134ee9faebd4d0cb0783a42be1ce9e440fbc"
	ifindBaseURL    = "https://quantapi.51ifind.com/api/v1"
	tokenCacheTTL   = 86400 // 1天
	logMaxBytes     = 1 * 1024 * 1024 // 1MB
	logKeepBytes    = 500 * 1024       // 保留最近 500KB
)

var (
	skillDir string
	dataDir  string
)

func init() {
	exe, err := os.Executable()
	if err != nil {
		exe = os.Args[0]
	}
	exe, _ = filepath.EvalSymlinks(exe)
	skillDir = filepath.Dir(filepath.Dir(exe)) // <binary>/../
	dataDir = filepath.Join(skillDir, ".data")
	os.MkdirAll(dataDir, 0755)
}

// ═══════════════════════════════════════════════════
// 日志
// ═══════════════════════════════════════════════════

func logPath() string {
	return filepath.Join(dataDir, "ifind.log")
}

func rotateLog() {
	path := logPath()
	info, err := os.Stat(path)
	if err != nil || info.Size() <= int64(logMaxBytes) {
		return
	}
	data, err := os.ReadFile(path)
	if err != nil {
		return
	}
	// 保留最后 logKeepBytes
	if len(data) > logKeepBytes {
		data = data[len(data)-logKeepBytes:]
		// 找到第一个换行，避免截断行
		if idx := bytes.IndexByte(data, '\n'); idx >= 0 {
			data = data[idx+1:]
		}
	}
	os.WriteFile(path, data, 0644)
}

func logEntry(endpoint, status, errMsg, step string, latency time.Duration, trial bool) {
	rotateLog()
	f, err := os.OpenFile(logPath(), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return
	}
	defer f.Close()

	ts := time.Now().Format("2006-01-02 15:04:05")
	msg := fmt.Sprintf("[%s] endpoint=%s status=%s latency=%dms trial=%v",
		ts, endpoint, status, latency.Milliseconds(), trial)
	if errMsg != "" {
		msg += fmt.Sprintf(" error=%q step=%s", errMsg, step)
	}
	fmt.Fprintln(f, msg)
}

// ═══════════════════════════════════════════════════
// .env 加载
// ═══════════════════════════════════════════════════

func loadEnv() map[string]string {
	envFile := filepath.Join(skillDir, ".env")
	env := make(map[string]string)
	f, err := os.Open(envFile)
	if err != nil {
		return env
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			val := strings.TrimSpace(parts[1])
			// 去除引号
			val = strings.Trim(val, `"'`)
			env[key] = val
			os.Setenv(key, val)
		}
	}
	return env
}

// ═══════════════════════════════════════════════════
// getUserID — 多平台硬件指纹
// ═══════════════════════════════════════════════════

func getUserID() (string, error) {
	idFile := filepath.Join(dataDir, "user_id")

	// 优先使用已持久化的 user_id
	if data, err := os.ReadFile(idFile); err == nil && len(data) > 0 {
		return strings.TrimSpace(string(data)), nil
	}

	fingerprint := getHardwareFingerprint()

	// SHA256 → ifind_<20chars>
	hash := sha256.Sum256([]byte("ifind_" + fingerprint))
	userID := fmt.Sprintf("ifind_%x", hash[:])[:26] // "ifind_" + 20 hex chars

	os.WriteFile(idFile, []byte(userID), 0644)
	return userID, nil
}

func getHardwareFingerprint() string {
	switch runtime.GOOS {
	case "linux":
		return getLinuxFingerprint()
	case "darwin":
		return getDarwinFingerprint()
	case "windows":
		return getWindowsFingerprint()
	default:
		return getFallbackFingerprint()
	}
}

func getLinuxFingerprint() string {
	// /sys/class/net/*/address 取 MAC
	matches, _ := filepath.Glob("/sys/class/net/*/address")
	for _, m := range matches {
		data, err := os.ReadFile(m)
		if err != nil {
			continue
		}
		addr := strings.TrimSpace(string(data))
		if addr != "" && addr != "00:00:00:00:00:00" {
			return addr
		}
	}
	// 备选: CPU info
	if data, err := os.ReadFile("/proc/cpuinfo"); err == nil {
		for _, line := range strings.Split(string(data), "\n") {
			if strings.Contains(line, "model name") || strings.Contains(line, "Serial") {
				parts := strings.SplitN(line, ":", 2)
				if len(parts) == 2 {
					return strings.TrimSpace(parts[1])
				}
			}
		}
	}
	return getFallbackFingerprint()
}

func getDarwinFingerprint() string {
	// ioreg 取硬件 UUID
	out, err := exec.Command("ioreg", "-rd1", "-c", "IOPlatformExpertDevice").Output()
	if err == nil {
		for _, line := range strings.Split(string(out), "\n") {
			if strings.Contains(line, "IOPlatformUUID") {
				parts := strings.Split(line, `"`)
				for i, p := range parts {
					if p == "IOPlatformUUID" && i+2 < len(parts) {
						return parts[i+2]
					}
				}
			}
		}
	}
	// 备选: ifconfig
	out, err = exec.Command("ifconfig").Output()
	if err == nil {
		for _, line := range strings.Split(string(out), "\n") {
			if strings.Contains(line, "ether ") {
				fields := strings.Fields(line)
				for i, f := range fields {
					if f == "ether" && i+1 < len(fields) {
						return fields[i+1]
					}
				}
			}
		}
	}
	return getFallbackFingerprint()
}

func getWindowsFingerprint() string {
	// 读注册表 MachineGuid
	out, err := exec.Command("reg", "query",
		`HKLM\SOFTWARE\Microsoft\Cryptography`,
		"/v", "MachineGuid").Output()
	if err == nil {
		for _, line := range strings.Split(string(out), "\n") {
			if strings.Contains(line, "MachineGuid") {
				fields := strings.Fields(line)
				if len(fields) >= 3 {
					return fields[len(fields)-1]
				}
			}
		}
	}
	return getFallbackFingerprint()
}

func getFallbackFingerprint() string {
	hostname, _ := os.Hostname()
	user := os.Getenv("USER")
	if user == "" {
		user = os.Getenv("USERNAME")
	}
	return hostname + "-" + user + "-fallback"
}

// ═══════════════════════════════════════════════════
// HTTP 工具
// ═══════════════════════════════════════════════════

var httpClient = &http.Client{Timeout: 30 * time.Second}

func httpPost(url string, headers map[string]string, body []byte) ([]byte, error) {
	req, err := http.NewRequest("POST", url, bytes.NewReader(body))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	for k, v := range headers {
		req.Header.Set(k, v)
	}

	resp, err := httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	return io.ReadAll(resp.Body)
}

// ═══════════════════════════════════════════════════
// skillpayCharge — 计费验证
// ═══════════════════════════════════════════════════

func skillpayCharge(userID string) (trial bool, err error) {
	start := time.Now()

	payload, _ := json.Marshal(map[string]string{"user_id": userID})
	data, err := httpPost(ifindBillingURL+"/charge",
		map[string]string{"X-Api-Secret": ifindAPISecret}, payload)
	if err != nil {
		logEntry("charge", "error", err.Error(), "charge", time.Since(start), false)
		return false, fmt.Errorf("计费服务请求失败: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		logEntry("charge", "error", "invalid json response", "charge", time.Since(start), false)
		return false, fmt.Errorf("计费服务返回异常: %s", string(data))
	}

	success, _ := result["success"].(bool)
	if success {
		isTrial, _ := result["trial"].(bool)
		if isTrial {
			fmt.Fprintf(os.Stderr, "[TRIAL] %s\n", string(data))
		}
		return isTrial, nil
	}

	// 余额不足
	paymentURL, _ := result["payment_url"].(string)
	balance, _ := result["balance"]
	logEntry("charge", "error", "insufficient balance", "charge", time.Since(start), false)
	errResp := map[string]interface{}{
		"error":       "余额不足，请点击链接充值 USDT 后重试",
		"balance":     fmt.Sprintf("%v USDT", balance),
		"payment_url": paymentURL,
	}
	writeJSON(os.Stdout, errResp)
	os.Exit(1)
	return false, nil // unreachable
}

// ═══════════════════════════════════════════════════
// getAccessToken — 缓存 + 自动刷新
// ═══════════════════════════════════════════════════

func getAccessToken(refreshToken string) (string, error) {
	cacheFile := filepath.Join(dataDir, "access_token")

	// 检查缓存
	if info, err := os.Stat(cacheFile); err == nil {
		age := time.Since(info.ModTime()).Seconds()
		if age < tokenCacheTTL {
			if data, err := os.ReadFile(cacheFile); err == nil && len(data) > 0 {
				return strings.TrimSpace(string(data)), nil
			}
		}
	}

	start := time.Now()

	// 请求新 token
	data, err := httpPost(ifindBaseURL+"/get_access_token",
		map[string]string{"refresh_token": refreshToken}, []byte("{}"))
	if err != nil {
		logEntry("get_access_token", "error", err.Error(), "get_token", time.Since(start), false)
		return "", fmt.Errorf("获取 access_token 失败: %v", err)
	}

	var result map[string]interface{}
	if err := json.Unmarshal(data, &result); err != nil {
		logEntry("get_access_token", "error", "invalid json", "get_token", time.Since(start), false)
		return "", fmt.Errorf("获取 access_token 响应异常: %s", string(data))
	}

	// 解析 data.access_token
	dataObj, ok := result["data"].(map[string]interface{})
	if !ok {
		logEntry("get_access_token", "error", "no data field", "get_token", time.Since(start), false)
		return "", fmt.Errorf("获取 access_token 失败，请检查 IFIND_REFRESH_TOKEN 是否有效")
	}
	token, ok := dataObj["access_token"].(string)
	if !ok || token == "" {
		logEntry("get_access_token", "error", "no access_token", "get_token", time.Since(start), false)
		return "", fmt.Errorf("获取 access_token 失败，请检查 IFIND_REFRESH_TOKEN 是否有效")
	}

	os.WriteFile(cacheFile, []byte(token), 0644)
	return token, nil
}

func clearTokenCache() {
	os.Remove(filepath.Join(dataDir, "access_token"))
}

// ═══════════════════════════════════════════════════
// callAPI — 调用 iFinD API
// ═══════════════════════════════════════════════════

func callAPI(accessToken, endpoint, jsonBody string) ([]byte, error) {
	url := ifindBaseURL + "/" + endpoint
	headers := map[string]string{
		"access_token":    accessToken,
		"Accept-Encoding": "gzip,deflate",
	}
	return httpPost(url, headers, []byte(jsonBody))
}

// ═══════════════════════════════════════════════════
// main
// ═══════════════════════════════════════════════════

func writeJSON(w io.Writer, v interface{}) {
	enc := json.NewEncoder(w)
	enc.SetEscapeHTML(false)
	enc.Encode(v)
}

func exitError(msg string) {
	writeJSON(os.Stdout, map[string]string{"error": msg})
	os.Exit(1)
}

func main() {
	// 参数校验
	if len(os.Args) < 3 {
		writeJSON(os.Stdout, map[string]string{
			"error": "用法: ifind-api <api_endpoint> <json_body>",
		})
		os.Exit(1)
	}

	apiEndpoint := os.Args[1]
	jsonBody := os.Args[2]

	// 加载 .env
	loadEnv()

	refreshToken := os.Getenv("IFIND_REFRESH_TOKEN")
	if refreshToken == "" {
		exitError("缺少环境变量 IFIND_REFRESH_TOKEN，请设置后重试")
	}

	// 获取 user_id
	userID, err := getUserID()
	if err != nil {
		exitError(fmt.Sprintf("获取 user_id 失败: %v", err))
	}

	start := time.Now()

	// Step 1: 计费验证
	trial, err := skillpayCharge(userID)
	if err != nil {
		exitError(err.Error())
	}

	// Step 2: 获取 access_token
	accessToken, err := getAccessToken(refreshToken)
	if err != nil {
		exitError(err.Error())
	}

	// Step 3: 调用 iFinD API
	result, err := callAPI(accessToken, apiEndpoint, jsonBody)
	if err != nil {
		logEntry(apiEndpoint, "error", err.Error(), "api_call", time.Since(start), trial)
		exitError(fmt.Sprintf("API 调用失败: %v", err))
	}

	// 检查 errorcode = -1302 (token 过期)，自动重试
	var apiResult map[string]interface{}
	if err := json.Unmarshal(result, &apiResult); err == nil {
		if code, ok := apiResult["errorcode"]; ok {
			var errorCode float64
			switch v := code.(type) {
			case float64:
				errorCode = v
			case json.Number:
				f, _ := v.Float64()
				errorCode = f
			}
			if errorCode == -1302 {
				clearTokenCache()
				accessToken, err = getAccessToken(refreshToken)
				if err != nil {
					logEntry(apiEndpoint, "error", err.Error(), "api_call", time.Since(start), trial)
					exitError(err.Error())
				}
				result, err = callAPI(accessToken, apiEndpoint, jsonBody)
				if err != nil {
					logEntry(apiEndpoint, "error", err.Error(), "api_call", time.Since(start), trial)
					exitError(fmt.Sprintf("API 调用失败 (重试): %v", err))
				}
			}
		}
	}

	logEntry(apiEndpoint, "ok", "", "", time.Since(start), trial)
	fmt.Println(string(result))
}
