import { singleFilterSingleOption } from '@models/generic'

export interface EmailPreferences {
  company_categories: singleFilterSingleOption[] | string[]
  email_notifications_enabled: boolean
  emails_per_day_count: number | null
  near_deadline_notifications_enabled: boolean
  program_categories: singleFilterSingleOption[] | string[]
  regions: singleFilterSingleOption[] | string[]
}
