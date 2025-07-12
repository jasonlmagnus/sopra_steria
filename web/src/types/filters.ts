export type FilterOption = {
  value: string | number;
  label: string;
};

export type FilterConfig = {
  name: string;
  label:string;
  type: 'select' | 'range' | 'text' | 'multiselect';
  options?: FilterOption[]; // For select and multiselect types
  defaultValue?: any;
  min?: number; // For range type
  max?: number; // For range type
  step?: number; // For range type
}; 