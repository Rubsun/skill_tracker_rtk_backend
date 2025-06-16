import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';

const API_URL = 'http://localhost:8000/api/v1';

const EmployeeDashboardPage = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useContext(AuthContext);

    useEffect(() => {
        const fetchAssignedTasks = async () => {
            if (!user?.token) {
                setLoading(false);
                return;
            }

            setLoading(true);
            try {
                const response = await fetch(`${API_URL}/tasks/`, {
                    headers: { 'Authorization': `Bearer ${user.token}` }
                });

                if (!response.ok) {
                    throw new Error('Не удалось загрузить задачи.');
                }
                
                const data = await response.json();
                const tasksData = Array.isArray(data) ? data[1] || [] : (data?.items || data || []);
                setTasks(tasksData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchAssignedTasks();
    }, [user]);

    if (loading) return <LoadingSpinner />;
    if (error) return <div className="text-red-500">Произошла ошибка. Пожалуйста, попробуйте позже.</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold text-secondary-dark mb-6">Мои задачи</h1>
            {tasks.length === 0 ? (
                <p className="text-secondary">У вас пока нет задач.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {tasks.map(task => {
                        const deadlineDate = task.deadline ? new Date(task.deadline) : null;
                        const now = new Date();
                        let badgeColor = 'bg-green-500';
                        let badgeText = '';
                        if (deadlineDate) {
                            const diffDays = Math.ceil((deadlineDate - now) / (1000 * 60 * 60 * 24));
                            if (diffDays < 0) {
                                badgeColor = 'bg-red-500';
                                badgeText = 'Просрочено';
                            } else if (diffDays === 0) {
                                badgeColor = 'bg-orange-500';
                                badgeText = 'Сегодня';
                            } else if (diffDays <= 3) {
                                badgeColor = 'bg-yellow-400';
                                badgeText = `${diffDays} дн.`;
                            } else {
                                badgeText = `${diffDays} дн.`;
                            }
                        }
                        const cardClasses = "rounded-xl p-6 flex flex-col justify-between bg-white/40 dark:bg-zinc-800/50 backdrop-blur-md shadow-lg hover:-translate-y-1 hover:shadow-2xl transition transform";
                        return (
                            <div key={task.id} className={cardClasses}>
                                {deadlineDate && (
                                    <span className={`inline-block px-2 py-0.5 text-xs text-white rounded-full self-start ${badgeColor}`}>{badgeText}</span>
                                )}
                                <div>
                                    <h2 className="text-xl font-semibold text-secondary-dark mb-2">{task.title}</h2>
                                    <p className="text-sm text-secondary mb-4">{task.description}</p>
                                    <p className="text-sm text-gray-600 mb-2">Дедлайн: {task.deadline ? new Date(task.deadline).toLocaleString() : 'Не задан'}</p>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${task.progress}%` }}></div>
                                    </div>
                                    <p className="text-xs text-gray-600 text-right">{task.progress}% завершено</p>
                                </div>
                                <Link
                                    to={`/employee/task/${task.id}`}
                                    className="mt-4 btn-gradient w-full text-center"
                                >
                                    Открыть задачу
                                </Link>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default EmployeeDashboardPage;