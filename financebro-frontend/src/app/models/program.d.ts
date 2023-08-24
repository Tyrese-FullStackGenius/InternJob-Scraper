import { singleFilterSingleOption } from '@models/generic'
import { ComponentType } from '@angular/cdk/overlay'

export interface Program {
  application_url: string | null
  cities_mapped: ProgramCity[]
  company: ProgramCompany
  deadline: Date | null
  deadline_text: string | null
  description: string | null
  eligibility: string | null
  favorite?: boolean
  id: number
  is_application_open: boolean | null
  program_type: string | null
  program_type_description: string | null
  region: ProgramRegion
  title: string
  url: string
}

export interface ProgramCompany {
  category: string
  id: number
  name: string
}

export interface ProgramRegion {
  code: string
  name: string
}

export interface ProgramCity {
  country: string
  name: string
}

export interface ProgramNote {
  created_date: string
  note: string
}

export interface UserProgram {
  application_close_reason: string | null
  id: number
  is_application_closed: boolean | null
  is_application_submitted: boolean | null
  is_favorite: boolean | true
  is_online_test_taken: boolean | null
  is_personal_interview_taken: boolean | null
  is_pre_recorded_video_interview_taken: boolean | null
  notes?: ProgramNote[]
  program: Program
}

export interface CommunityReportedData {
  does_ask_for_cover_letter: {
    reported_true: number
    reported_false: number
    unreported: number
  }
  was_there_no_online_test: {
    reported_true: number
    reported_false: number
    unreported: number
  }
  was_there_no_pre_recorded_video_interview_stage: {
    reported_true: number
    reported_false: number
    unreported: number
  }
  online_test_questions: string[]
  pre_recorded_video_interview_format: string[]
  personal_interview_questions: string[]
}

export interface UserProgramCommunityReportedData {
  program_id: number
  community_reported_data: CommunityReportedData
}

export interface ProgramsResource {
  favorite_programs: number[]
  total: number
  programs: Program[]
}

export interface AvailableFilters {
  company_category: singleFilterSingleOption[]
  company: singleFilterSingleOption[]
  country: singleFilterSingleOption[]
  program_category: singleFilterSingleOption[]
  region: singleFilterSingleOption[]
  is_application_open: singleFilterSingleOption[]
  does_ask_for_cover_letter: singleFilterSingleOption[]
}

export interface AvailableFiltersResource {
  filters: AvailableFilters
}

export interface ProgramsFilters {
  category: string
}

export interface Dictionary<T> {
  [key: string]: T
}

export interface UserProgramNoteDto {
  program_id: number
  note: string
}

export interface ToggleProgramFavoriteDto {
  program_id: number
  set_favorite: boolean
}

export type ProgramActions =
  | 'submitted'
  | 'online_test'
  | 'pre_recorded_video_interview'
  | 'personal_interview'
  | 'close'

export interface UserProgramPipelineActionDto {
  program_id: number
  action: ProgramActions
  value: boolean
  optional_info: object
}

export interface UpgradeAccountDto {
  redirect_url: string
}

export interface CloseDialogData {
  application_close_reason: string
}

export interface OnlineTestDialogData {
  online_test_questions: string
}

export interface PersonalInterviewDialogData {
  was_there_no_online_test: boolean
  was_there_no_pre_recorded_video_interview_stage: boolean
  personal_interview_questions: string
}

export interface PreRecordedVideoInterviewDialogData {
  was_there_no_online_test: boolean
  pre_recorded_video_interview_format: string
}

export interface SubmittedDialogData {
  does_ask_for_cover_letter: boolean
}

export interface DialogInitData<T> {
  action: ProgramActions
  component: ComponentType<T>
  data:
    | CloseDialogData
    | OnlineTestDialogData
    | PersonalInterviewDialogData
    | PreRecordedVideoInterviewDialogData
    | SubmittedDialogData
}
