from enum import Enum
import typing as t

from ninja import ModelSchema
from ninja import Schema
from pydantic import Field

from internships.models import City
from internships.models import Company
from internships.models import Country
from internships.models import Program
from internships.models import Region
from internships.models import UserProgram
from internships.models import UserProgramNotes


class CompanySchema(ModelSchema):
    class Config:
        model = Company
        model_fields = ['id', 'name', 'category']


class RegionSchema(ModelSchema):
    class Config:
        model = Region
        model_fields = ['code', 'name']


class CitySchema(ModelSchema):
    class Config:
        model = City
        model_fields = ['name', 'country']


class CountrySchema(ModelSchema):
    class Config:
        model = Country
        model_fields = ['name', 'code']


class ProgramSchema(ModelSchema):
    company: CompanySchema
    region: t.Optional[RegionSchema]
    locations: t.Optional[t.List[str]]
    cities_mapped: t.Optional[t.List[CitySchema]]
    countries_mapped: t.Optional[t.List[CountrySchema]]

    class Config:
        model = Program
        model_fields = [
            'id', 'title', 'deadline', 'deadline_text', 'eligibility', 'program_type', 'program_type_description',
            'is_application_open', 'url', 'category', 'application_url', 'extra_data', 'is_visa_sponsorship_provided'
        ]

    @staticmethod
    def resolve_locations(obj):
        return obj.cities


class SingleFilterSingleOptionSchema(Schema):
    value: t.Union[int, str]
    viewValue: t.Union[str, bool]


class AvailableFiltersSchema(Schema):
    filters: dict[str, t.List[SingleFilterSingleOptionSchema]]


class ProgramsOutSchema(Schema):
    total: int
    programs: t.List[ProgramSchema]
    applied_filters: dict[str, t.Union[str, bool]]
    favorite_programs: t.Optional[t.List[int]]


class ToggleProgramFavoriteInSchema(Schema):
    program_id: int
    set_favorite: t.Optional[bool] = True


class UserProgramPreferencesSchema(Schema):
    regions: t.List[str]
    company_categories: t.List[str]
    program_categories: t.List[str]


class UserEmailPreferencesSchema(Schema):
    email_notifications_enabled: bool
    regions: t.List[str]
    company_categories: t.List[str]
    program_categories: t.List[str]
    emails_per_day_count: t.Optional[int]
    near_deadline_notifications_enabled: bool


class UserProgramPipelineActionEnum(str, Enum):
    submitted = 'submitted'
    online_test = 'online_test'
    pre_recorded_video_interview = 'pre_recorded_video_interview'
    personal_interview = 'personal_interview'
    close = 'close'


class UserProgramPipelineOptionalInfoEnum(str, Enum):
    does_ask_for_cover_letter = 'does_ask_for_cover_letter'
    was_there_no_online_test = 'was_there_no_online_test'
    online_test_questions = 'online_test_questions'
    pre_recorded_video_interview_format = 'pre_recorded_video_interview_format'
    was_there_no_pre_recorded_video_interview_stage = 'was_there_no_pre_recorded_video_interview_stage'
    personal_interview_questions = 'personal_interview_questions'
    application_close_reason = 'application_close_reason'


class UserProgramPipelineActionInSchema(Schema):
    program_id: int
    action: UserProgramPipelineActionEnum
    value: bool
    optional_info: dict[UserProgramPipelineOptionalInfoEnum, t.Union[bool, str]]


class UserProgramDetailOutSchema(ModelSchema):
    program: ProgramSchema
    current_stage: t.Optional[str] = None

    class Config:
        model = UserProgram
        model_fields = [
            'id', 'is_favorite', 'is_application_submitted', 'is_online_test_taken',
            'is_pre_recorded_video_interview_taken', 'is_personal_interview_taken', 'is_application_closed',
            'application_close_reason', 'is_application_submitted_datetime', 'is_online_test_taken_datetime',
            'is_pre_recorded_video_interview_taken_datetime', 'is_personal_interview_taken_datetime',
            'is_application_closed_datetime'
        ]


class ProgramSchemaWithDescription(ProgramSchema):
    description: str


class UserProgramDetailOutWithDescriptionSchema(UserProgramDetailOutSchema):
    program: ProgramSchemaWithDescription


class UserProgramOutSchema(Schema):
    total: int
    programs: t.List[UserProgramDetailOutSchema]


class UserProgramNoteInSchema(Schema):
    program_id: int
    note: str


class UserProgramNoteSchema(ModelSchema):
    class Config:
        model = UserProgramNotes
        model_fields = ['note', 'created_date']


class UserProgramDetailOutWithNotesAndDescriptionSchema(UserProgramDetailOutWithDescriptionSchema):
    notes: t.List[UserProgramNoteSchema]


class ProgramCommunityReportedDataFieldsEnum(str, Enum):
    does_ask_for_cover_letter = 'does_ask_for_cover_letter'
    was_there_no_online_test = 'was_there_no_online_test'
    online_test_questions = 'online_test_questions'
    was_there_no_pre_recorded_video_interview_stage = 'was_there_no_pre_recorded_video_interview_stage'
    pre_recorded_video_interview_format = 'pre_recorded_video_interview_format'
    personal_interview_questions = 'personal_interview_questions'


class CommunityReportedDataSingleFieldCountSchema(Schema):
    reported_true: int
    reported_false: int
    unreported: int


class ProgramCommunityReportedDataOutSchema(Schema):
    program_id: int
    community_reported_data: dict[
        UserProgramPipelineOptionalInfoEnum,
        t.Union[list, CommunityReportedDataSingleFieldCountSchema]
    ]


class ProgramsFiltersSchema(Schema):
    company_id: t.Optional[int] = None
    company_category: t.Optional[str] = None
    program_category: t.Optional[str] = None
    region: t.Optional[str] = None
    is_application_open: bool = True
    does_ask_for_cover_letter: t.Optional[str] = None
    countries: t.List[str] = Field(None, alias="countries")
    is_visa_sponsorship_provided: t.Optional[bool] = None
    search_term: t.Optional[str] = None


class DashboardStatsSchema(Schema):
    summer_internships_count: int
    offcycle_internships_count: int
    spring_internships_count: int
    total_open_opportunities: int
    recent_programs: ProgramsOutSchema


class SingleCompanyStatsSchema(Schema):
    name: str
    total_programs_count: int
    open_programs_count: int
