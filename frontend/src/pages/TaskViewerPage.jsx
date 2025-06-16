import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';
import { toast } from 'react-hot-toast';

const API_URL = 'http://localhost:8000/api/v1';

const TaskViewerPage = () => {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    
    const [task, setTask] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Local state for edits
    const [status, setStatus] = useState('');
    const [progress, setProgress] = useState(0);
    const [comments, setComments] = useState([]);
    const [commentsLoading, setCommentsLoading] = useState(true);
    const [newComment, setNewComment] = useState('');
    const [editingId, setEditingId] = useState(null);
    const [editingText, setEditingText] = useState('');

    useEffect(() => {
        const fetchTask = async () => {
            if (!user?.token || !taskId) {
                setLoading(false);
                return;
            }
            try {
                setLoading(true);
                const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });
                if (!response.ok) throw new Error('Failed to fetch task details.');
                const data = await response.json();
                setTask(data);
                // Initialize local state for editing
                setStatus(data.status);
                setProgress(data.progress);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTask();

        // Fetch comments
        const fetchComments = async () => {
            if (!user?.token || !taskId) return;
            try {
                const res = await fetch(`${API_URL}/comments/?task_id=${taskId}`, {
                    headers: { 'Authorization': `Bearer ${user.token}` }
                });
                if (!res.ok) throw new Error('Failed to fetch comments');
                const data = await res.json();
                // backend returns [total, list] or list; handle both
                const list = Array.isArray(data) && Array.isArray(data[1]) ? data[1] : data;
                // sort by created_at ascending
                list.sort((a,b)=> new Date(a.created_at)-new Date(b.created_at));
                setComments(list);
            } catch (e) {
                console.error(e);
            } finally {
                setCommentsLoading(false);
            }
        };

        fetchComments();
    }, [taskId, user]);
    
    const handleUpdate = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await fetch(`${API_URL}/tasks/${taskId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify({
                    status: status,
                    progress: Number(progress),
                }),
            });
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to update task.');
            }
            const updatedTask = await response.json();
            setTask(updatedTask);
            setStatus(updatedTask.status);
            setProgress(updatedTask.progress);
            toast.success('Данные сохранены');
        } catch (err) {
            console.error(err);
        }
    };

    const handleAddComment = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;
        try {
            const res = await fetch(`${API_URL}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify({ text: newComment, task_id: taskId })
            });
            if (!res.ok) throw new Error('Failed to add comment');
            const created = await res.json();
            setComments(prev => [...prev, created]);
            setNewComment('');
            toast.success('Комментарий добавлен');
        } catch (err) {
            console.error(err);
        }
    };

    const isCurrentUserAssigned = user && task && user.id === task.employee_id;

    if (loading) return <div className="flex justify-center items-center h-screen"><LoadingSpinner /></div>;
    if (error) return <div className="text-center text-red-500 p-4">Произошла ошибка. Пожалуйста, попробуйте позже.</div>;
    if (!task) return <div className="text-center p-4">Task not found.</div>;

    return (
        <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
            <div className="mb-6">
                <Link to={user?.role === 'manager' ? '/manager/dashboard' : '/employee/dashboard'} className="text-primary hover:underline">&larr; Назад к панели</Link>
            </div>
            <header className="mb-8 p-6 bg-white rounded-lg shadow">
                <h1 className="text-4xl font-extrabold mb-2 text-secondary-dark">{task.title}</h1>
                <p className="text-lg text-gray-600">{task.description}</p>
                <div className="mt-4 text-sm text-gray-500">
                    Дедлайн: {new Date(task.deadline).toLocaleString()}
                </div>
            </header>
            
            <main className="space-y-8">
                <div className="p-6 bg-white rounded-lg shadow">
                    <h2 className="text-2xl font-bold mb-4">Детали задачи</h2>
                    <div className="space-y-4">
                        <div>
                            <span className="font-semibold">Статус:</span> {{pending:'Ожидание',inprogress:'В работе',done:'Завершена'}[task.status] || task.status}
                        </div>
                        <div>
                            <span className="font-semibold">Прогресс:</span>
                            <div className="w-full bg-gray-200 rounded-full h-4 dark:bg-gray-700 mt-1">
                                <div className="bg-blue-600 h-4 rounded-full" style={{ width: `${task.progress}%` }}></div>
                            </div>
                             <div className="text-right text-sm font-medium text-gray-600">{task.progress}%</div>
                        </div>
                    </div>
                </div>

                {isCurrentUserAssigned && (
                    <div className="p-6 bg-white rounded-lg shadow">
                         <h2 className="text-2xl font-bold mb-4">Обновить прогресс</h2>
                         <form onSubmit={handleUpdate} className="space-y-4">
                             <div>
                                <label htmlFor="status" className="label">Статус</label>
                                <select id="status" value={status} onChange={e => setStatus(e.target.value)} className="select select-bordered w-full">
                                    <option value="pending">Ожидание</option>
                                    <option value="inprogress">В работе</option>
                                    <option value="done">Завершена</option>
                                </select>
                             </div>
                             <div>
                                 <label htmlFor="progress" className="label">Прогресс ({progress}%)</label>
                                <input id="progress" type="range" min="0" max="100" value={progress} onChange={e => setProgress(e.target.value)} className="range range-primary"/>
                             </div>
                             <button type="submit" className="btn btn-primary">Сохранить</button>
                             {error && <p className="text-red-500 mt-2">{error}</p>}
                         </form>
                    </div>
                )}

                {/* Comments Section */}
                <div className="p-6 bg-white rounded-lg shadow">
                    <h2 className="text-2xl font-bold mb-4">Комментарии</h2>
                    {commentsLoading ? (
                        <LoadingSpinner />
                    ) : (
                        <>
                            {comments.length === 0 ? (
                                <p className="text-gray-500 mb-4">Комментариев нет.</p>
                            ) : (
                                <ul className="space-y-4 mb-6">
                                    {comments.map(c => {
                                        const authorName = c.user_id === user.id ? 'Вы' : (c.user_id === task.manager_id ? 'Менеджер' : 'Сотрудник');
                                        return (
                                            <li key={c.id} className="border rounded p-3 bg-gray-50">
                                                <div className="flex items-center justify-between text-sm text-gray-500 mb-1">
                                                    <span className="font-medium">{authorName}</span>
                                                    <span>{new Date(c.created_at).toLocaleString()}</span>
                                                </div>
                                                {editingId === c.id ? (
                                                    <div className="space-y-2">
                                                        <textarea className="textarea textarea-bordered w-full" rows="3" value={editingText} onChange={e=>setEditingText(e.target.value)} />
                                                        <div className="flex gap-2">
                                                            <button className="btn btn-sm btn-primary" onClick={async()=>{
                                                                try{
                                                                    const res=await fetch(`${API_URL}/comment/${c.id}`,{method:'PUT',headers:{'Content-Type':'application/json','Authorization':`Bearer ${user.token}`},body:JSON.stringify({text:editingText})});
                                                                    if(!res.ok) throw new Error('Fail');
                                                                    const updated=await res.json();
                                                                    setComments(prev=>prev.map(cm=>cm.id===c.id?updated:cm));
                                                                    setEditingId(null);
                                                                    toast.success('Обновлено');
                                                                }catch(err){console.error(err);}
                                                            }}>Сохранить</button>
                                                            <button className="btn btn-sm" onClick={()=>setEditingId(null)}>Отмена</button>
                                                        </div>
                                                    </div>
                                                ) : (
                                                    <>
                                                        <p className="whitespace-pre-wrap text-gray-800 {c._deleted ? 'italic text-gray-400':''}">{c._deleted? 'Комментарий удален': c.text}</p>
                                                        { !c._deleted && c.user_id===user.id && (
                                                            <div className="mt-2 flex gap-3 text-sm">
                                                                <button className="text-primary" onClick={()=>{setEditingId(c.id);setEditingText(c.text);}}>Редактировать</button>
                                                                <button className="text-error" onClick={async()=>{
                                                                    if(!confirm('Удалить комментарий?')) return;
                                                                    try{
                                                                        const res=await fetch(`${API_URL}/comment/${c.id}`,{method:'DELETE',headers:{'Authorization':`Bearer ${user.token}`}});
                                                                        if(!res.ok) throw new Error('Fail');
                                                                        setComments(prev=>prev.map(cm=>cm.id===c.id?{...cm,_deleted:true}:cm));
                                                                        toast.success('Комментарий удалён');
                                                                    }catch(err){console.error(err);}
                                                                }}>Удалить</button>
                                                            </div>
                                                        )}
                                                    </>
                                                )}
                                            </li>
                                        );
                                    })}
                                </ul>
                            )}

                            {/* Add comment */}
                            <form onSubmit={handleAddComment} className="space-y-3">
                                <textarea
                                    className="textarea textarea-bordered w-full"
                                    rows="3"
                                    placeholder="Добавьте комментарий..."
                                    value={newComment}
                                    onChange={e => setNewComment(e.target.value)}
                                />
                                <div className="text-right">
                                    <button type="submit" className="btn btn-primary" disabled={!newComment.trim()}>Отправить</button>
                                </div>
                            </form>
                        </>
                    )}
                </div>
            </main>
        </div>
    );
};

export default TaskViewerPage;