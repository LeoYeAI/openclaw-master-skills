"""
XGO 机器人控制库
统一入口，自动选择设备类型
"""

# 直接导入所有类
from .xgolib_dog import XGO_DOG
from .xgolib_rider import XGO_RIDER


__version__ = '1.0.0'
__all__ = ['XGO', 'XGO_DOG', 'XGO_RIDER']

def XGO(version="auto",port="/dev/ttyAMA0", baud=115200,  verbose=False):
    """
    统一的XGO类工厂函数
    
    Args:
        port: 串口设备路径
        baud: 波特率
        version: 设备版本 
            "auto" - 自动检测
            "xgomini" - XGO-MINI
            "xgolite" - XGO-LITE  
            "xgomini3w" - XGO-MINI3W
            "xgorider" - XGO-RIDER
        verbose: 是否显示调试信息
    """
    if version == "auto":
        try:

            temp_dog: XGO_DOG = XGO_DOG(port, baud, version="xgomini", verbose=verbose)
            firmware: str = temp_dog.read_firmware()
            print(f"Detected firmware: {firmware}")
            
            if firmware and firmware[0] == 'R':
                print("Auto-detected: XGO-RIDER")
                return XGO_RIDER(port, baud, version="xgorider", verbose=verbose)
            elif firmware and firmware[0] in ['M', 'L', 'W']:
                print(f"Auto-detected: XGO-{firmware[0]}")
                return XGO_DOG(port, baud, version="auto", verbose=verbose)
            else:
                print("Auto-detection failed, using default: XGO-MINI")
                return XGO_DOG(port, baud, version="xgomini", verbose=verbose)
                
        except Exception as e:
            print(f"Auto detection failed: {e}, using default: XGO-MINI")
            return XGO_DOG(port, baud, version="xgomini", verbose=verbose)
    
    elif version in ["xgomini", "xgolite", "xgomini3w","mini", "lite", "mini3w"]:
        return XGO_DOG(port, baud, version=version, verbose=verbose)
    
    elif version == "xgorider" or version == "rider":
        return XGO_RIDER(port, baud, version=version, verbose=verbose)
    
    else:
        print(f"Warning: Unknown version '{version}', using 'xgomini' instead")
        return XGO_DOG(port, baud, version="xgomini", verbose=verbose)