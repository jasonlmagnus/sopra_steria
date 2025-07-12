import React from 'react';
import './Banner.css';

type BannerProps = {
  message: React.ReactNode;
  type?: 'info' | 'warning' | 'error' | 'success';
  className?: string;
};

const Banner: React.FC<BannerProps> = ({ message, type = 'info', className = '' }) => {
  return (
    <div className={`banner banner--${type} ${className}`}>
      {message}
    </div>
  );
};

export default Banner; 