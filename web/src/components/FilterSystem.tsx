import React from 'react';
import { useFilters } from '../hooks/useFilters';
import type { FilterConfig } from '../types/filters';
import './FilterSystem.css';

interface FilterSystemProps {
  config: FilterConfig[];
  data: any; // Data from API, containing dynamic options
}

export function FilterSystem({ config, data }: FilterSystemProps) {
  const { filters, setFilter } = useFilters();

  const renderFilter = (filter: FilterConfig) => {
    const { name, label, type, options, min, max, step } = filter;
    const value = filters[name] || '';

    switch (type) {
      case 'select': {
        const dynamicOptions = data[name + 'Options'] || options || [];
        return (
          <div key={name} className="filter-item">
            <label htmlFor={name} className="filter-label">{label}</label>
            <select
              id={name}
              value={value}
              onChange={(e) => setFilter(name, e.target.value)}
              className="filter-select"
            >
              {dynamicOptions.map((opt: any) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        );
      }
      case 'range':
        return (
          <div key={name} className="filter-item">
            <label htmlFor={name} className="filter-label">{label}: {value}</label>
            <input
              type="range"
              id={name}
              min={min}
              max={max}
              step={step}
              value={value}
              onChange={(e) => setFilter(name, Number(e.target.value))}
              className="filter-range"
            />
          </div>
        );
      case 'text':
        return (
          <div key={name} className="filter-item">
            <label htmlFor={name} className="filter-label">{label}</label>
            <input
              type="text"
              id={name}
              value={value}
              onChange={(e) => setFilter(name, e.target.value)}
              className="filter-input"
            />
          </div>
        );
      case 'multiselect': {
        const selectedValues = value || [];
        return (
          <div key={name} className="filter-item">
            <label className="filter-label">{label}</label>
            <div className="filter-multiselect-group">
              {(options || []).map(opt => (
                <div key={opt.value} className="filter-checkbox-item">
                  <input
                    type="checkbox"
                    id={`${name}-${opt.value}`}
                    checked={selectedValues.includes(opt.value)}
                    onChange={(e) => {
                      const newSelection = e.target.checked
                        ? [...selectedValues, opt.value]
                        : selectedValues.filter((v: any) => v !== opt.value);
                      setFilter(name, newSelection);
                    }}
                  />
                  <label htmlFor={`${name}-${opt.value}`}>{opt.label}</label>
                </div>
              ))}
            </div>
          </div>
        )
      }
      default:
        return null;
    }
  };

  return (
    <div className="filter-system">
      <h2 className="heading--section">Filters</h2>
      <div className="filter-controls-container">
        {config.map(renderFilter)}
      </div>
    </div>
  );
}

export default FilterSystem; 