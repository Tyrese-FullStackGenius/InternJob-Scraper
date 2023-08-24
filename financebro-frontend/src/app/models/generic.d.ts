export interface singleFilterSingleOption {
  value: string
  viewValue: string | boolean
}

export interface AllPreferences {
  company_category: singleFilterSingleOption[]
  company: singleFilterSingleOption[]
  country: singleFilterSingleOption[]
  is_application_open: singleFilterSingleOption[]
  does_ask_for_cover_letter: singleFilterSingleOption[]
  program_category: singleFilterSingleOption[]
  region: singleFilterSingleOption[]
}
