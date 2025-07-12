import { createContext } from 'react';

export interface FiltersState {
  [key: string]: any;
}

interface FilterContextValue {
  filters: FiltersState;
  setFilter: (name: string, value: any) => void;
  setAllFilters: (filters: FiltersState) => void;
}

export const FilterContext = createContext<FilterContextValue | undefined>(
  undefined,
); 