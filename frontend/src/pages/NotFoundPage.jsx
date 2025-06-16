import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-background text-center px-4">
            <svg className="w-16 h-16 text-primary mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
             <h1 className="text-4xl md:text-6xl font-bold text-secondary-dark mb-2">404</h1>
            <h2 className="text-2xl md:text-3xl font-semibold text-secondary mb-6">Страница не найдена</h2>
            <p className="text-secondary mb-8 max-w-md">
                Упс! Похоже, такой страницы не существует или она была перемещена.
            </p>
            <Link
                to="/"
                className="px-6 py-3 bg-primary hover:bg-primary-dark text-white font-semibold rounded-md transition duration-150 ease-in-out"
            >
                На главную
            </Link>
        </div>
    );
};

export default NotFoundPage;