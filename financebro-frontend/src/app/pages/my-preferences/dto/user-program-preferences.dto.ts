import { singleFilterSingleOption } from '@models/generic'

export interface UserProgramPreferences {
  company_categories: singleFilterSingleOption[] | string[]
  program_categories: singleFilterSingleOption[] | string[]
  regions: singleFilterSingleOption[] | string[]
}
