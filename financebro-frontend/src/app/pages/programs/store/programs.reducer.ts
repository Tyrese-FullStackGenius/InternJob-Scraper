import { createReducer, on } from '@ngrx/store'
import { Program, AvailableFiltersResource } from '@models/program'
import { Params } from '@angular/router'
import { ProgramsActions } from '@pages/programs/store/programs.actions'

export const programsFeatureKey = 'programs'

export interface State {
  favorite_programs: number[]
  programs: Program[]
  total: number

  filters: Params
  isLoading: boolean

  availableFilters: AvailableFiltersResource
}

export const initialState: State = {
  favorite_programs: [],
  programs: [],
  total: -1,
  isLoading: false,
  filters: {},
  availableFilters: {
    filters: {
      company_category: [],
      company: [],
      country: [],
      program_category: [],
      region: [],
      is_application_open: [],
      does_ask_for_cover_letter: [],
    },
  },
}

export const programsReducer = createReducer(
  initialState,

  on(ProgramsActions.getAllPrograms, (state, { filters }): State => {
    return {
      ...state,
      favorite_programs: [],
      programs: [],
      total: -1,
      isLoading: true,
      filters: filters ? filters : {},
    }
  }),

  on(ProgramsActions.getAllProgramsSuccess, (state, { favorite_programs, programs, total }): State => {
    return {
      ...state,
      favorite_programs,
      programs,
      total,
      isLoading: false,
    }
  }),

  on(ProgramsActions.getAllProgramsFailure, (state): State => {
    return {
      ...state,
      favorite_programs: [],
      programs: [],
      total: -1,
      isLoading: false,
    }
  }),

  on(ProgramsActions.getAllAvailableFilters, (state): State => {
    return {
      ...state,
      isLoading: true,
      availableFilters: {
        filters: {
          company_category: [],
          company: [],
          country: [],
          program_category: [],
          region: [],
          is_application_open: [],
          does_ask_for_cover_letter: [],
        },
      },
    }
  }),

  on(ProgramsActions.addProgramToFavorites, (state, { programId }): State => {
    if (state.favorite_programs.includes(programId)) {
      return state
    }
    return {
      ...state,
      favorite_programs: [...state.favorite_programs, programId],
    }
  }),

  on(ProgramsActions.removeProgramFromFavorites, (state, { programId }): State => {
    if (!state.favorite_programs.includes(programId)) {
      return state
    }
    return {
      ...state,
      favorite_programs: state.favorite_programs.filter(id => id !== programId),
    }
  }),

  on(ProgramsActions.updateFavoriteProgramsList, (state): State => {
    const programs = state.programs.map(program => ({
      ...program,
      favorite: state.favorite_programs.includes(program.id),
    }))
    return {
      ...state,
      programs: programs,
    }
  }),

  on(ProgramsActions.getAllAvailableFiltersSuccess, (state, { filters }): State => {
    return {
      ...state,
      isLoading: false,
      availableFilters: {
        filters: { ...filters },
      },
    }
  }),

  on(ProgramsActions.getAllAvailableFiltersFailure, (state): State => {
    return {
      ...state,
      availableFilters: {
        filters: {
          company_category: [],
          company: [],
          country: [],
          program_category: [],
          region: [],
          is_application_open: [],
          does_ask_for_cover_letter: [],
        },
      },
      isLoading: false,
    }
  }),
)
