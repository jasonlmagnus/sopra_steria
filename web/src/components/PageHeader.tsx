import React from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({ title, description }) => {
  return (
    <div className="container--section">
      <h1 className="heading--page">{title}</h1>
      {description && <p className="text--body">{description}</p>}
    </div>
  );
}; 