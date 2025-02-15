from typing import Optional, Literal

from pydantic import field_validator, ConfigDict, BaseModel, Field

from api.conf.base_config import BaseConfig
from api.enums import OpenaiWebChatModels, OpenaiApiChatModels
from api.enums.options import OpenaiWebFileUploadStrategyOption
from utils.common import SingletonMeta

_TYPE_CHECKING = False

default_openai_web_model_code_mapping = {
    "gpt_3_5": "gpt-4o-mini",
    "gpt_4": "gpt-4",
    "gpt_4o": "gpt-4o",
    "o1": "o1",
    "o1_mini": "o1-mini"
}


class CommonSetting(BaseModel):
    print_sql: bool = False
    print_traceback: bool = True
    create_initial_admin_user: bool = True
    initial_admin_user_username: str = 'admin'
    initial_admin_user_password: str = 'password'

    @field_validator("initial_admin_user_password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password too short")
        return v


class HttpSetting(BaseModel):
    host: str = '127.0.0.1'
    port: int = Field(8000, ge=1, le=65535)
    cors_allow_origins: list[str] = ['http://localhost:8000', 'http://localhost:5173', 'http://127.0.0.1:8000',
                                     'http://127.0.0.1:5173']


class DataSetting(BaseModel):
    data_dir: str = './data'
    database_url: str = 'sqlite+aiosqlite:///data/database.db'
    mongodb_url: str = 'mongodb://cws:password@mongo:27017'
    mongodb_db_name: str = 'cws'
    run_migration: bool = True
    max_file_upload_size: int = Field(100 * 1024 * 1024, ge=0)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v):
        if not v.startswith('sqlite+aiosqlite:///'):
            raise ValueError("Only support sqlite: 'sqlite+aiosqlite:///'")
        return v


class AuthSetting(BaseModel):
    jwt_secret: str = 'MODIFY_THIS_TO_RANDOM_SECURE_STRING'
    jwt_lifetime_seconds: int = Field(3 * 24 * 3600, ge=1)
    cookie_max_age: int = Field(3 * 24 * 3600, ge=1)
    user_secret: str = 'MODIFY_THIS_TO_ANOTHER_RANDOM_SECURE_STRING'


class OpenaiWebChatGPTSetting(BaseModel):
    enabled: bool = True
    is_plus_account: bool = True
    enable_team_subscription: bool = False
    team_account_id: Optional[str] = None
    chatgpt_base_url: Optional[str] = None
    proxy: Optional[str] = None
    wss_proxy: Optional[str] = None
    enable_arkose_endpoint: bool = False
    arkose_endpoint_base: Optional[str] = None
    common_timeout: int = Field(20, ge=1,
                                description="Increase this value if timeout error occurs.")  # connect, read, write
    ask_timeout: int = Field(600, ge=1)
    sync_conversations_on_startup: bool = False
    sync_conversations_schedule: bool = False
    sync_conversations_schedule_interval_hours: int = Field(12, ge=1)
    enabled_models: list[OpenaiWebChatModels] = ["gpt_3_5", "gpt_4", "gpt_4o","o1","o1_mini"]
    model_code_mapping: dict[OpenaiWebChatModels, str] = default_openai_web_model_code_mapping
    file_upload_strategy: OpenaiWebFileUploadStrategyOption = OpenaiWebFileUploadStrategyOption.browser_upload_only
    max_completion_concurrency: int = Field(1, ge=1)
    disable_uploading: bool = False

    @field_validator("chatgpt_base_url")
    @classmethod
    def chatgpt_base_url_end_with_slash(cls, v):
        if v is not None and not v.endswith('/'):
            v += '/'
        return v

    @field_validator("arkose_endpoint_base")
    @classmethod
    def arkose_endpoint_base_end_with_slash(cls, v):
        if v is not None and not v.endswith('/'):
            v += '/'
        return v

    @field_validator("model_code_mapping")
    @classmethod
    def check_all_model_key_appears(cls, v):
        if not set(OpenaiWebChatModels) == set(v.keys()):
            # add missing keys
            for model in OpenaiWebChatModels:
                if model not in v:
                    assert model in default_openai_web_model_code_mapping
                    v[model] = default_openai_web_model_code_mapping[model]
        return v


class OpenaiApiSetting(BaseModel):
    enabled: bool = True
    openai_base_url: str = 'https://api.openai.com/v1/'
    proxy: Optional[str] = None
    connect_timeout: int = Field(10, ge=1)
    read_timeout: int = Field(20, ge=1)
    enabled_models: list[OpenaiApiChatModels] = ["gpt_3_5", "gpt_4", "gpt_4o","o1","o1_mini"]
    model_code_mapping: dict[OpenaiApiChatModels, str] = {
        "gpt_3_5": "gpt-4o-mini",
        "gpt_4": "gpt-4",
        "gpt_4o": "gpt-4o",
        "o1": "o1",
        "o1_mini": "o1-mini"
    }


class LogSetting(BaseModel):
    console_log_level: Literal['INFO', 'DEBUG', 'WARNING'] = 'INFO'


class StatsSetting(BaseModel):
    ask_stats_ttl: int = 90 * 24 * 60 * 60  # 90 days
    request_stats_ttl: int = 30 * 24 * 60 * 60  # 30 days. -1 means never expire
    request_stats_filter_keywords: list[str] = ['/status']


class ConfigModel(BaseModel):
    openai_web: OpenaiWebChatGPTSetting = OpenaiWebChatGPTSetting()
    openai_api: OpenaiApiSetting = OpenaiApiSetting()
    common: CommonSetting = CommonSetting()
    http: HttpSetting = HttpSetting()
    data: DataSetting = DataSetting()
    auth: AuthSetting = AuthSetting()
    stats: StatsSetting = StatsSetting()
    log: LogSetting = LogSetting()


class Config(BaseConfig[ConfigModel], metaclass=SingletonMeta):
    if _TYPE_CHECKING:
        openai_web: OpenaiWebChatGPTSetting = OpenaiWebChatGPTSetting()
        openai_api: OpenaiApiSetting = OpenaiApiSetting()
        common: CommonSetting = CommonSetting()
        http: HttpSetting = HttpSetting()
        log: LogSetting = LogSetting()
        stats: StatsSetting = StatsSetting()
        data: DataSetting = DataSetting()
        auth: AuthSetting = AuthSetting()

    def __init__(self, load_config: bool = True):
        super().__init__(ConfigModel, "config.yaml", load_config=load_config)
