#!/usr/bin/env python3
import os
import sys
from enum import Enum
from typing import Dict
import inspect

import yaml
import platform


class YamlUtil:

    @staticmethod
    def load(path, config: Dict = {}) -> Dict:
        try:
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                return config
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
                for key, value in config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            pass
        return config

    @staticmethod
    def save(path, config: Dict) -> Dict:
        try:
            with open(path, "w", encoding="utf-8") as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        except:
            pass
        return config


class BaseEnum:

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        clsModule = cls.__module__
        cls_path = inspect.getfile(cls)
        clsFullName = f"{cls.__module__}.{cls.__name__}"
        cls_dirpath = os.path.dirname(cls_path)  # .../src
        clsModulePath = clsModule.replace(".", "\\")
        current_dir = os.path.dirname(os.path.abspath(__file__))  # .../src
        config_path = os.path.join(cls_dirpath, "config.yaml")
        config = YamlUtil.load(config_path)
        cls.init(config)
        env = config.get("env")
        if env:
            env_config_path = os.path.join(cls_dirpath, f"config-{env}.yaml")
            env_config = YamlUtil.load(env_config_path)
            cls.init(env_config)

    @classmethod
    def init(cls, config=None):
        clsName = cls.__name__
        clsConfig = config and config.get(clsName)
        if clsConfig:
            for config_key, config_value in clsConfig.items():
                new_config_key = config_key = config_key.upper().replace("-", "_")
                if hasattr(cls, new_config_key):
                    setattr(cls, new_config_key, config_value)


class ApiEnum(BaseEnum):
    API_KEY = None

    API_SECRET_KEY = None

    DATABASE_URL = ""

    BASE_URL_OPEN_API = ""

    BASE_URL_OPEN_H5 = ""

    BASE_URL_HEALTH = ""

    OPEN_TOKEN = ""

    TOKEN = ""

    DEFAULT__REQUEST_TIMEOUT = 120

    DEFAULT__PAGE_SIZE = 5

    DEFAULT__PAGE_SIZE_MAX = 65536

    GET_DOWNLOAD_URL__URL = BASE_URL_OPEN_API + "/api/tos/get-download-url"


class ConstantEnum(BaseEnum):
    class SourceEnum(Enum):
        ARK_CLAW = "ARK_CLAW"
        JVS_CLAW = "JVS_CLAW"
        LIGHT_CLAW = "LIGHT_CLAW"
        WUHONG = "WUHONG"
        COZE = "COZE"
        SKILL_HUB = "SKILL_HUB"
        CLAW_HUB = "CLAW_HUB"
        FEISHU = "FEISHU"
        DINGTALK = "DINGTALK"
        WEIXIN = "WEIXIN"
        YUANBAO = "YUANBAO"
        WECOM = "WECOM"
        QQBOT = "QQBOT"

    APP__ID = ""

    APP__SOURCE = SourceEnum.CLAW_HUB.value

    IS_DEBUG = False

    CURRENT__OPEN_ID = ""

    CURRENT__USER_NAME = ""

    CURRENT__TENTANT_CODE = ""

    FEISHU_APP__ID = ""

    FEISHU_APP__SECRET = ""

    FEISHU_APP__RECEIVE_ID = ""

    DEFAULT__SCENE_CODE = ""

    DEFAULT__SKILL_HUB_NAME = APP__SOURCE

    DEFAULT__SKILL_PLATFORM_NAME = ""

    DEFAULT__OUTPUT_LEVEL = "json"

    SUPPORTED_FORMATS = ["mp4", "avi", "mov"]

    MAX_FILE_SIZE_MB = 10

    @staticmethod
    def is_debug():
        return platform.system() != 'Linux' and ConstantEnum.IS_DEBUG

    @classmethod
    def init(cls, config=None):
        super().init(config)
        openclaw_sender_open_id = os.environ.get("OPENCLAW_SENDER_OPEN_ID")
        openclaw_sender_username = os.environ.get("OPENCLAW_SENDER_USERNAME")
        feishu_open_id = os.environ.get("FEISHU_OPEN_ID")
        if openclaw_sender_open_id:
            cls.CURRENT__OPEN_ID = openclaw_sender_open_id
        if openclaw_sender_username:
            cls.CURRENT__USER_NAME = openclaw_sender_username
        if feishu_open_id:
            cls.FEISHU_APP__RECEIVE_ID = feishu_open_id

    class SceneCodeEnum(Enum):
        # 开放 #
        OPEN_HEALTH_AI_ANALYSIS = "OPEN_HEALTH_AI_ANALYSIS"
        OPEN_PERSON_RISK_ANALYSIS = "OPEN_PERSON_RISK_ANALYSIS"
        # 智眸 #
        PUBLIC_AREA_AI_ANALYSIS = "PUBLIC_AREA_AI_ANALYSIS"
        PERSONNEL_LEAVE_POST_MONITORING = "PERSONNEL_LEAVE_POST_MONITORING"
        CRAWL_MONITOR = "CRAWL_MONITOR"
        # 先兆感知 #
        XIAN_ZHAO_GAN_ZHI_DESK_LAMP = "XIAN_ZHAO_GAN_ZHI_DESK_LAMP"
        PET_ANALYSIS = "PET_ANALYSIS"
        CRAWL_ANALYSIS = "CRAWL_ANALYSIS"
        AQUARIUM_ANALYSIS = "AQUARIUM_ANALYSIS"
        PSYCHOLOGY_ANALYSIS = "PSYCHOLOGY_ANALYSIS"
        AUTISM_ANALYSIS = "AUTISM_ANALYSIS"
        DIET_ANALYSIS = "DIET_ANALYSIS"
        DRIVE_ANALYSIS = "DRIVE_ANALYSIS"
        SPORT_ANALYSIS = "SPORT_ANALYSIS"
        EMOTION_ANALYSIS = "EMOTION_ANALYSIS"
        STUDY_ANALYSIS = "STUDY_ANALYSIS"
        INFANT_SAFETY_MONITORING_ANALYSIS = "INFANT_SAFETY_MONITORING"
        PHONE_USAGE_MONITORING_ANALYSIS = "PHONE_USAGE_MONITORING"
        INCONTINENCE_ALERT_ANALYSIS = "INCONTINENCE_ALERT"
        RESPIRATORY_SYMPTOM_RECOGNITION_ANALYSIS = "RESPIRATORY_SYMPTOM_RECOGNITION"
        ELECTRIC_VEHICLE_DETECTION_ANALYSIS = "ELECTRIC_VEHICLE_DETECTION"
        SMOKING_DETECTION_ANALYSIS = "SMOKING_DETECTION"
        PET_DETECTION_FEEDER_ANALYSIS = "PET_DETECTION_FEEDER"
        PET_HEALTH_MONITORING_ANALYSIS = "PET_HEALTH_MONITORING"
        STROKE_RISK_SCREENING_ANALYSIS = "STROKE_RISK_SCREENING"
        HUMAN_DETECTION_ANALYSIS = "HUMAN_DETECTION"
        STRANGER_RECOGNITION_ANALYSIS = "STRANGER_RECOGNITION"
        FOCUS_ANALYSIS_ANALYSIS = "FOCUS_ANALYSIS"
        HUMAN_POSTURE_RECOGNITION_ANALYSIS = "HUMAN_POSTURE_RECOGNITION"
        HUMAN_EMOTION_RECOGNITION_ANALYSIS = "HUMAN_EMOTION_RECOGNITION"
        FIRE_SMOKE_DETECTION_ANALYSIS = "FIRE_SMOKE_DETECTION"
        BASIC_OBJECT_DETECTION_ANALYSIS = "BASIC_OBJECT_DETECTION"
        CHILD_DANGEROUS_BEHAVIOR_RECOGNITION_ANALYSIS = "CHILD_DANGEROUS_BEHAVIOR_RECOGNITION"
        PET_RESTRICTED_AREA_WARNING_ANALYSIS = "PET_RESTRICTED_AREA_WARNING"
        SLEEP_QUALITY_ANALYSIS_ANALYSIS = "SLEEP_QUALITY_ANALYSIS"
        PET_DETECTION_ANALYSIS = "PET_DETECTION"
        PSYCHOLOGICAL_STRESS_ASSESSMENT_ANALYSIS = "PSYCHOLOGICAL_STRESS_ASSESSMENT"
        VISUAL_QA_ANALYSIS = "VISUAL_QA"
        PET_BODY_HEALTH_ANALYSIS = "PET_BODY_HEALTH_ANALYSIS"
        PET_BEHAVIOR_DETECTION_ANALYSIS = "PET_BEHAVIOR_DETECTION"
        INFANT_SUFFOCATION_WARNING_ANALYSIS = "INFANT_SUFFOCATION_WARNING"
        STRANGER_APPROACH_WARNING_ANALYSIS = "STRANGER_APPROACH_WARNING"
        IMAGE_QUALITY_DETECTION_ANALYSIS = "IMAGE_QUALITY_DETECTION"
        CHILD_EMOTION_RECOGNITION_ANALYSIS = "CHILD_EMOTION_RECOGNITION"
        OUTDOOR_MONITORING_ANALYSIS = "OUTDOOR_MONITORING"
        FALL_DETECTION_IMAGE_ANALYSIS = "FALL_DETECTION_IMAGE"
        CUSTOM_TIMELAPSE_ANALYSIS = "CUSTOM_TIMELAPSE"
        CONTACTLESS_VITAL_SIGNS_MONITORING_ANALYSIS = "CONTACTLESS_VITAL_SIGNS_MONITORING"
        VIDEO_SEARCH_ANALYSIS = "VIDEO_SEARCH"
        FAMILIAR_PERSON_RECOGNITION_ANALYSIS = "FAMILIAR_PERSON_RECOGNITION"
        TCM_CONSTITUTION_RECOGNITION_ANALYSIS = "TCM_CONSTITUTION_RECOGNITION"
        CONTACTLESS_HEALTH_RISK_DETECTION_ANALYSIS = "CONTACTLESS_HEALTH_RISK_DETECTION"
        UNACCOMPANIED_MONITORING_ANALYSIS = "UNACCOMPANIED_MONITORING"
        ELDERLY_FALL_DETECTION_ANALYSIS = "ELDERLY_FALL_DETECTION"
        PARKINSON_EPILEPSY_BEHAVIOR_RECOGNITION_ANALYSIS = "PARKINSON_EPILEPSY_BEHAVIOR_RECOGNITION"
        PET_BREED_INDIVIDUAL_RECOGNITION_ANALYSIS = "PET_BREED_INDIVIDUAL_RECOGNITION"
        ELDERLY_BED_EXIT_WANDERING_MONITORING_ANALYSIS = "ELDERLY_BED_EXIT_WANDERING_MONITORING"
        ARRHYTHMIA_EARLY_WARNING_ANALYSIS = "ARRHYTHMIA_EARLY_WARNING"
        FIRE_DETECTION_ANALYSIS = "FIRE_DETECTION"
        VISUAL_SUMMARY_ANALYSIS = "VISUAL_SUMMARY"
        PACKAGE_DETECTION_ANALYSIS = "PACKAGE_DETECTION"
        INFANT_BLANKET_KICK_MONITORING_ANALYSIS = "INFANT_BLANKET_KICK_MONITORING"
        PET_CALMING_TRIGGER_ANALYSIS = "PET_CALMING_TRIGGER"
        CAT_FACE_RECOGNITION_ANALYSIS = "CAT_FACE_RECOGNITION"
        INFANT_SLEEP_MONITORING_ANALYSIS = "INFANT_SLEEP_MONITORING"
        VIRTUAL_FENCE_INTRUSION_WARNING_ANALYSIS = "VIRTUAL_FENCE_INTRUSION_WARNING"
        FALL_DETECTION_VIDEO_ANALYSIS = "FALL_DETECTION_VIDEO"
        INFANT_CRY_ANALYSIS = "INFANT_CRY_ANALYSIS"
        PET_VOCAL_EMOTION_ANALYSIS = "PET_VOCAL_EMOTION_ANALYSIS"
        BIRD_RECOGNITION_ANALYSIS = "BIRD_RECOGNITION"
        FRAUD_CALL_IDENTIFICATION = "FRAUD_CALL_IDENTIFICATION"
        PLANT_SPECIES_RECOGNITION = "PLANT_SPECIES_RECOGNITION"
        PLANT_GROWTH_STAGE_RECOGNITION = "PLANT_GROWTH_STAGE_RECOGNITION"
        PLANT_DISEASE_RECOGNITION = "PLANT_DISEASE_RECOGNITION"
        PLANT_NUTRITION_DIAGNOSIS = "PLANT_NUTRITION_DIAGNOSIS"
        PLANT_WILTING_MONITORING = "PLANT_WILTING_MONITORING"
