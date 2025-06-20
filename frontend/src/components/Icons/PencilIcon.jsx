import React from 'react';

const PencilIcon = ({ size = "md" }) => {
    const sizeClasses = {
        sm: "w-4 h-4",
        md: "w-5 h-5", // Default size for this icon
        lg: "w-6 h-6",
    };
    return (
        <svg xmlns="http://www.w3.org/2000/svg" className={sizeClasses[size]} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.536L16.732 3.732z" />
        </svg>
    );
};

export default PencilIcon; 