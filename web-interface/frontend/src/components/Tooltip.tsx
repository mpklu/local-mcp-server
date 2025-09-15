import React, { useState } from 'react';
import { InformationCircleIcon } from '@heroicons/react/24/outline';

interface TooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

const Tooltip: React.FC<TooltipProps> = ({ content, children, position = 'top' }) => {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  };

  const getArrowPosition = () => {
    switch (position) {
      case 'top':
        return 'top-full left-1/2 -translate-x-1/2 -mt-1';
      case 'bottom':
        return 'bottom-full left-1/2 -translate-x-1/2 -mb-1';
      case 'left':
        return 'left-full top-1/2 -translate-y-1/2 -ml-1';
      case 'right':
        return 'right-full top-1/2 -translate-y-1/2 -mr-1';
      default:
        return 'top-full left-1/2 -translate-x-1/2 -mt-1';
    }
  };

  return (
    <span 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
      role="tooltip"
    >
      {children}
      
      {isVisible && (
        <div className={`absolute z-50 ${positionClasses[position]}`}>
          <div className="bg-gray-900 dark:bg-gray-700 text-white text-xs rounded-lg px-3 py-2 max-w-xs shadow-lg">
            {content}
            <div className={`absolute w-2 h-2 bg-gray-900 dark:bg-gray-700 transform rotate-45 ${getArrowPosition()}`} />
          </div>
        </div>
      )}
    </span>
  );
};

interface HelpIconProps {
  content: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export const HelpIcon: React.FC<HelpIconProps> = ({ content, position = 'top' }) => {
  return (
    <Tooltip content={content} position={position}>
      <InformationCircleIcon className="h-4 w-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 cursor-help" />
    </Tooltip>
  );
};

export default Tooltip;
