import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';

const API_URL = 'http://localhost:8000/api/v1';

const EditIcon = () => <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path></svg>;
const AssignIcon = () => <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path></svg>;
const ChartBarIcon = () => <svg className="w-5 h-5 inline mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M3 3a1 1 0 000 2v8a1 1 0 001 1h1.172l1.513 1.513a1 1 0 001.414 0l4-4a1 1 0 000-1.414l-1.586-1.586a1 1 0 00-1.414 0L10 10.586 8.707 9.293a1 1 0 00-1.414 0L3 13.586V5a1 1 0 00-.293-.707L2 3.586A1 1 0 001 4v9a1 1 0 001 1h12a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1-1zm14-1a1 1 0 00-1 1v10a1 1 0 001 1h1a1 1 0 001-1V3a1 1 0 00-1-1h-1z" clipRule="evenodd"></path></svg>;

const ManagerDashboardPage = () => {
    const [tasks, setTasks] = useState([]);
    const [employeeMap, setEmployeeMap] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const { user } = useContext(AuthContext);
    
    useEffect(() => {
        const fetchData = async () => {
            if (!user?.token) { setLoading(false); return; }
            setLoading(true);
            try {
                const tasksPromise = fetch(`${API_URL}/tasks/?skip=0&limit=100`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });

                const employeesPromise = fetch(`${API_URL}/employees`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });

                const [tasksResponse, employeesResponse] = await Promise.all([tasksPromise, employeesPromise]);
                
                if (!tasksResponse.ok) throw new Error('Failed to fetch tasks');
                if (!employeesResponse.ok) throw new Error('Failed to fetch employees');
                
                const tasksDataRaw = await tasksResponse.json();
                const tasksData = Array.isArray(tasksDataRaw) ? tasksDataRaw[1] || [] : (tasksDataRaw?.items || tasksDataRaw || []);

                const employeesRaw = await employeesResponse.json();
                const employeesList = Array.isArray(employeesRaw) && Array.isArray(employeesRaw[1]) ? employeesRaw[1] : employeesRaw;
                const map = {};
                for (const e of employeesList) {
                    const fullName = e.given_name ? `${e.given_name} ${e.family_name}` : e.email;
                    map[e.id] = fullName;
                }
                setEmployeeMap(map);

                setTasks(tasksData);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [user]);

    if (loading) return <LoadingSpinner />;
    if (error) return <div className="text-red-500">Произошла ошибка. Пожалуйста, попробуйте позже.</div>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Панель менеджера</h1>
                <Link to="/manager/task/new" className="btn-gradient">Создать задачу</Link>
            </div>
            
            <h2 className="text-2xl font-semibold mb-4">Мои задачи</h2>
            <div className="rounded-xl overflow-hidden bg-white/40 dark:bg-zinc-800/50 backdrop-blur-md shadow-lg">
                <table className="min-w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left">Название задачи</th>
                            <th className="px-6 py-3 text-left">Исполнитель</th>
                            <th className="px-6 py-3 text-left">Дедлайн</th>
                            <th className="px-6 py-3 text-left">Прогресс</th>
                            <th className="px-6 py-3 text-left">Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {tasks.map((task) => (
                            <tr key={task.id}>
                                <td className="px-6 py-4">{task.title}</td>
                                <td className="px-6 py-4">{employeeMap[task.employee_id] || task.employee_id || 'N/A'}</td>
                                <td className="px-6 py-4">
                                    {task.deadline ? (()=>{
                                        const deadline=new Date(task.deadline);
                                        const now=new Date();
                                        const diff=Math.ceil((deadline-now)/(1000*60*60*24));
                                        let color='bg-green-500';
                                        let text=`${diff} дн.`;
                                        if(diff<0){color='bg-red-500';text='Просрочено'}
                                        else if(diff===0){color='bg-orange-500';text='Сегодня'}
                                        else if(diff<=3){color='bg-yellow-400'}
                                        return <span className={`inline-block px-2 py-0.5 text-xs text-white rounded-full ${color}`}>{text}</span>;
                                    })(): '—'}
                                </td>
                                <td className="px-6 py-4">{task.progress}%</td>
                                <td className="px-6 py-4 space-x-2">
                                    <Link to={`/manager/task/edit/${task.id}`} className="btn btn-sm btn-ghost"><EditIcon /> Редактировать</Link>
                                    <Link to={`/manager/task/${task.id}`} className="btn btn-sm btn-primary"><ChartBarIcon /> Открыть</Link>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ManagerDashboardPage;