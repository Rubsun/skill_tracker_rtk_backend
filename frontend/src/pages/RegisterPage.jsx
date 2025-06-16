import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const RegisterPage = () => {
    const [givenName, setGivenName] = useState('');
    const [familyName, setFamilyName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [role, setRole] = useState('employee'); // Default role
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { register } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await register(email, givenName, familyName, password, role);
            // Decide where to redirect after registration
            // Redirecting to role-specific dashboard via home '/'
            navigate('/', { replace: true });
        } catch (err) {
            console.error("Registration failed:", err);
            // Показываем отдельное сообщение, если пользователь уже зарегистрирован
            if (err.message === 'REGISTER_USER_ALREADY_EXISTS' || err.message === 'REGISTER_USER_ALREDY_EXISTS') {
                setError('Пользователь с таким email уже существует.');
            } else {
                // Use a more specific error message from the API if available
                setError('Не удалось зарегистрироваться. Попробуйте ещё раз.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="card-auth p-8 w-full max-w-md">
                <h2 className="text-2xl font-bold text-center text-secondary-dark mb-6">Регистрация в Skill Tracker</h2>
                <form onSubmit={handleSubmit}>
                    {error && <p className="bg-error/10 text-error text-sm p-3 rounded mb-4">{error}</p>}
                    <div className="mb-4">
                        <label htmlFor="givenName" className="block text-sm font-medium text-secondary mb-1">Имя</label>
                        <input
                            type="text"
                            id="givenName"
                            value={givenName}
                            onChange={(e) => setGivenName(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent"
                            placeholder="Иван"
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="familyName" className="block text-sm font-medium text-secondary mb-1">Фамилия</label>
                        <input
                            type="text"
                            id="familyName"
                            value={familyName}
                            onChange={(e) => setFamilyName(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent"
                            placeholder="Иванов"
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="email" className="block text-sm font-medium text-secondary mb-1">Электронная почта</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent"
                            placeholder="you@company.com"
                        />
                    </div>
                    <div className="mb-4">
                        <label htmlFor="password" className="block text-sm font-medium text-secondary mb-1">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            minLength="6" // Example validation
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent"
                            placeholder="••••••••"
                        />
                    </div>
                    <div className="mb-6">
                        <label htmlFor="role" className="block text-sm font-medium text-secondary mb-1">Роль</label>
                        <select
                            id="role"
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent bg-white"
                        >
                            <option value="employee">Сотрудник</option>
                            <option value="manager">Менеджер</option>
                        </select>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded-md focus:outline-none focus:shadow-outline transition duration-150 ease-in-out flex items-center justify-center disabled:opacity-50"
                    >
                        {loading ? <LoadingSpinner /> : 'Зарегистрироваться'}
                    </button>
                </form>
                <p className="text-center text-secondary text-sm mt-6">
                    Уже есть аккаунт? <Link to="/login" className="text-primary hover:underline">Войти</Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;