# QFPay OpenAPI Skill

OpenClaw Skill for QFPay Payment API integration, providing comprehensive guidelines for payment processing, signature generation, and API usage.

## Overview

This skill provides complete documentation for integrating with QFPay OpenAPI, including:
- Environment configuration (Production, Testing, Sandbox)
- API request/response formats
- Signature generation algorithms
- Payment type codes
- Currency support
- Status codes and error handling

## Installation
clawdhub install HONGKONG-PAYMENT-QFPAY

## Configuration
```bash
export QFPAY_APPCODE="your_app_code_here"
export QFPAY_KEY="your_client_key_here"
export QFPAY_MCHID="your_merchant_id"  # Optional, depends on account setup
export QFPAY_ENV="sandbox"  # Options: prod, test, sandbox
```

## Usage Examples
"create an Alipay HK order for 1 HKD"
"Check order status for ORDER123"

## Project Structure

```
├── README.md       # Project documentation (this file)
└── skill.md        # OpenClaw Skill definition
```

## Features

- **Environment Management**: Support for Production, Testing, and Sandbox environments
- **Signature Generation**: Complete guide for MD5 and SHA256 signature algorithms
- **Payment Types**: Comprehensive list of supported payment methods
- **Error Handling**: Detailed status codes and troubleshooting guide
- **Code Examples**: Python, Java, JavaScript, and PHP implementations

## Payment Types Supported

- Alipay (Web, WAP, In-App, MPM, CPM)
- WeChat Pay (Web QR, JSAPI, H5, Mini Program, In-App, MPM, CPM)
- PayMe (Web, WAP, MPM, CPM)
- UnionPay (QuickPass, WAP, Web)
- FPS (Faster Payment System)
- Octopus
- Visa / Mastercard
- Apple Pay

## Currencies Supported

HKD, CNY, USD, EUR, SGD, JPY, AUD, CAD, MYR, THB, IDR, AED, MMK

## Rate Limits

- 100 requests per second (RPS)
- 400 requests per minute per merchant

Exceeding limits returns HTTP 429 (Too Many Requests).

## Technical Support

- **Email**: technical.support@qfpay.com
- **Documentation**: https://sdk.qfapi.com

## License
MIT

This skill is provided for QFPay API integration purposes.
