import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';
import { PlusIcon, PencilIcon, TrashIcon } from '../components/Icons'; // Assuming you have icons
import { toast } from 'react-hot-toast';

const API_URL = 'http://localhost:8000/api/v1'; // Base API URL for backend endpoints

// --- Sub-components for the Editor ---

const ItemRenderer = ({ item, onEdit, onDelete }) => (
    <li className="flex justify-between items-center p-3 bg-gray-50 border rounded-md mb-2 shadow-sm">
        <div>
            <span className="block text-xs font-semibold text-primary uppercase">{item.item_type}</span>
            <span className="font-medium text-gray-800">{item.title}</span>
        </div>
        <div className="space-x-3">
            <button onClick={() => onEdit(item)} className="text-gray-500 hover:text-primary-dark">
                <PencilIcon />
            </button>
            <button onClick={() => onDelete(item.id)} className="text-gray-500 hover:text-error-dark">
                <TrashIcon />
            </button>
        </div>
    </li>
);

const LessonForm = ({ item, setItem }) => (
    <>
        <div>
            <label htmlFor="lessonTitle" className="block text-sm font-medium">Lesson Title</label>
            <input id="lessonTitle" type="text" value={item.title} onChange={(e) => setItem({ ...item, title: e.target.value })} className="w-full input" />
        </div>
        <div>
            <label htmlFor="lessonContent" className="block text-sm font-medium">Content (Markdown supported)</label>
            <textarea id="lessonContent" value={item.content} onChange={(e) => setItem({ ...item, content: e.target.value })} rows="8" className="w-full input" />
        </div>
    </>
);

const TaskForm = ({ item, setItem }) => {
    const handleOptionChange = (index, text) => {
        const newOptions = [...item.options];
        newOptions[index].text = text;
        setItem({ ...item, options: newOptions });
    };

    const handleCorrectChange = (index) => {
        const newOptions = item.options.map((opt, i) => ({
            ...opt,
            is_correct: item.task_type === 'single_choice' ? i === index : (i === index ? !opt.is_correct : opt.is_correct),
        }));
        setItem({ ...item, options: newOptions });
    };

    const addOption = () => {
        setItem({ ...item, options: [...item.options, { text: '', is_correct: false }] });
    };

    const removeOption = (index) => {
        const newOptions = item.options.filter((_, i) => i !== index);
        setItem({ ...item, options: newOptions });
    };

    return (
        <>
            <div>
                <label htmlFor="taskTitle" className="block text-sm font-medium">Task Title</label>
                <input id="taskTitle" type="text" value={item.title} onChange={(e) => setItem({ ...item, title: e.target.value })} className="w-full input" />
            </div>
             <div>
                <label htmlFor="taskQuestion" className="block text-sm font-medium">Question</label>
                <textarea id="taskQuestion" value={item.question} onChange={(e) => setItem({ ...item, question: e.target.value })} rows="3" className="w-full input" />
            </div>
            
            {(item.task_type === 'single_choice' || item.task_type === 'multiple_choice') && (
                 <div>
                    <h4 className="text-md font-medium mb-2">Options</h4>
                    {item.options.map((opt, index) => (
                        <div key={index} className="flex items-center gap-2 mb-2">
                            <input 
                                type={item.task_type === 'single_choice' ? 'radio' : 'checkbox'}
                                name="correct_option"
                                checked={opt.is_correct}
                                onChange={() => handleCorrectChange(index)}
                            />
                            <input 
                                type="text" 
                                value={opt.text} 
                                onChange={(e) => handleOptionChange(index, e.target.value)}
                                className="w-full input input-sm"
                                placeholder={`Option ${index + 1}`}
                            />
                            <button type="button" onClick={() => removeOption(index)} className="text-gray-500 hover:text-error-dark"><TrashIcon size="sm"/></button>
                        </div>
                    ))}
                    <button type="button" onClick={addOption} className="btn btn-ghost btn-sm mt-2">Add Option</button>
                 </div>
            )}
        </>
    );
};


const TaskEditorPage = () => {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);

    const [task, setTask] = useState({
        title: '',
        description: '',
        deadline: '',
        employee_id: '',
        status: 'pending',
        progress: 0,
    });
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const isEditing = Boolean(taskId);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const response = await fetch(`${API_URL}/employees`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });
                if (!response.ok) throw new Error('Failed to fetch users');
                const data = await response.json();
                const usersList = Array.isArray(data) && Array.isArray(data[1]) ? data[1] : data;
                setUsers(usersList);
            } catch (err) {
                setError(err.message);
            }
        };

        const fetchTask = async () => {
            if (!isEditing) return;
            setLoading(true);
            try {
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });
                if (!response.ok) throw new Error('Failed to fetch task details');
                const data = await response.json();
                setTask({
                    ...data,
                    deadline: data.deadline ? new Date(data.deadline).toISOString().substring(0, 16) : '',
                });
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };
        
        if (user?.token) {
            fetchUsers();
            fetchTask();
        }
    }, [taskId, user, isEditing]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setTask(prev => ({ ...prev, [name]: value }));
    };
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const url = isEditing ? `${API_URL}/tasks/${taskId}` : `${API_URL}/tasks/`;
        const method = isEditing ? 'PUT' : 'POST';
        
        // Ensure deadline is in ISO format if it exists
        const taskData = {
            ...task,
            progress: Number(task.progress),
            deadline: task.deadline ? new Date(task.deadline).toISOString() : null,
        };

        // For PUT, only send non-null fields
        const payload = isEditing ? Object.fromEntries(Object.entries(taskData).filter(([_, v]) => v != null)) : taskData;


        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(payload),
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to save the task');
            }
            
            toast.success(`Задача ${isEditing ? 'обновлена' : 'создана'}`);
            navigate('/manager/dashboard');
        } catch (err) {
            console.error(err);
            toast.error('Не удалось сохранить');
        } finally {
            setLoading(false);
        }
    };

    if (loading && !task.title) return <LoadingSpinner />;
    if (error) return <div className="text-red-500">Произошла ошибка. Пожалуйста, попробуйте позже.</div>;

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">{isEditing ? 'Редактирование задачи' : 'Создание задачи'}</h1>
            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label htmlFor="title" className="label">Название</label>
                    <input type="text" name="title" id="title" value={task.title} onChange={handleChange} className="input input-bordered w-full" required />
                </div>
                <div>
                    <label htmlFor="description" className="label">Описание</label>
                    <textarea name="description" id="description" value={task.description} onChange={handleChange} className="textarea textarea-bordered w-full"></textarea>
                </div>
                <div>
                    <label htmlFor="employee_id" className="label">Исполнитель</label>
                    <select name="employee_id" id="employee_id" value={task.employee_id} onChange={handleChange} className="select select-bordered w-full" required>
                        <option value="" disabled>Выберите исполнителя</option>
                        {users.map(u => (
                            <option key={u.id} value={u.id}>
                                {u.given_name ? `${u.given_name} ${u.family_name}` : u.email} ({u.email})
                            </option>
                        ))}
                    </select>
                </div>
                <div>
                    <label htmlFor="deadline" className="label">Дедлайн</label>
                    <input type="datetime-local" name="deadline" id="deadline" value={task.deadline} onChange={handleChange} className="input input-bordered w-full" />
                </div>
                <div>
                    <label htmlFor="status" className="label">Статус</label>
                    <select name="status" id="status" value={task.status} onChange={handleChange} className="select select-bordered w-full">
                        <option value="pending">Ожидание</option>
                        <option value="inprogress">В работе</option>
                        <option value="done">Завершена</option>
                    </select>
                </div>
                <div>
                    <label htmlFor="progress" className="label">Прогресс ({task.progress}%)</label>
                    <input type="range" name="progress" id="progress" min="0" max="100" value={task.progress} onChange={handleChange} className="range range-primary" />
                </div>
                <div className="flex justify-end gap-4">
                    <button type="button" onClick={() => navigate(-1)} className="btn btn-ghost">Отмена</button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? 'Сохранение...' : (isEditing ? 'Сохранить' : 'Создать')}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default TaskEditorPage;