import { useState, type ReactNode, useCallback } from 'react';
import { FilterContext, type FiltersState } from './FilterContextValue';

interface FilterProviderProps {
  children: ReactNode;
}

export function FilterProvider({ children }: FilterProviderProps) {
  const [filters, setFilters] = useState<FiltersState>({});

  const setFilter = useCallback((name: string, value: any) => {
    setFilters(prev => ({...prev, [name]: value}));
  }, []);

  const setAllFilters = useCallback((newFilters: FiltersState) => {
    setFilters(newFilters);
  }, []);

  const value = {
    filters,
    setFilter,
    setAllFilters,
  };

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}
