import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://localhost:8000/api/v1';

// --- Item Viewer Components ---

const LessonViewer = ({ item }) => (
    <div className="prose max-w-none p-6 bg-white rounded-lg shadow-sm border">
        <h2 className="text-2xl font-bold mb-4">{item.title}</h2>
        <ReactMarkdown>{item.content}</ReactMarkdown>
    </div>
);

const TaskViewer = ({ item, user, onTaskSubmit }) => {
    const [submission, setSubmission] = useState(null); // Local state for user's answer
    const [result, setResult] = useState(null); // Result from API
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!submission) return;

        setSubmitting(true);
        setError('');

        try {
            const payload = item.task_type === 'long_answer' 
                ? { answer_text: submission }
                : { selected_option_ids: submission };

            const response = await fetch(`${API_URL}/tasks/${item.id}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || 'Failed to submit answer.');

            setResult(data);
            onTaskSubmit(item.id, data);
        } catch (err) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    };
    
    const renderResult = () => {
        if (!result) return null;
        const isCorrect = result.is_correct;
        const bgColor = isCorrect ? 'bg-success-light' : 'bg-error-light';
        const textColor = isCorrect ? 'text-success-dark' : 'text-error-dark';

        return (
            <div className={`p-4 mt-4 rounded-md ${bgColor} ${textColor}`}>
                <h4 className="font-bold">{isCorrect ? 'Correct!' : 'Incorrect'}</h4>
                {result.score !== undefined && <p>Score: {result.score}</p>}
            </div>
        );
    };

    return (
        <div className="p-6 bg-white rounded-lg shadow-sm border">
            <h2 className="text-xl font-bold mb-1">{item.title}</h2>
            <p className="text-gray-700 mb-4">{item.question}</p>

            <form onSubmit={handleSubmit}>
                {item.task_type === 'long_answer' && (
                    <textarea 
                        className="w-full input" 
                        rows="6"
                        value={submission || ''}
                        onChange={(e) => setSubmission(e.target.value)}
                        disabled={!!result}
                    />
                )}

                {item.task_type === 'single_choice' && (
                    <div className="space-y-2">
                        {item.options.map(opt => (
                            <label key={opt.id} className="flex items-center p-3 border rounded-md has-[:checked]:bg-primary-light has-[:checked]:border-primary">
                                <input 
                                    type="radio" 
                                    name={`task-${item.id}`}
                                    className="radio radio-primary"
                                    onChange={() => setSubmission([opt.id])}
                                    disabled={!!result}
                                />
                                <span className="ml-3">{opt.text}</span>
                            </label>
                        ))}
                    </div>
                )}
                
                {item.task_type === 'multiple_choice' && (
                     <div className="space-y-2">
                        {item.options.map(opt => (
                            <label key={opt.id} className="flex items-center p-3 border rounded-md has-[:checked]:bg-primary-light has-[:checked]:border-primary">
                                <input 
                                    type="checkbox"
                                    className="checkbox checkbox-primary"
                                    onChange={(e) => {
                                        const currentSubs = submission || [];
                                        if (e.target.checked) {
                                            setSubmission([...currentSubs, opt.id]);
                                        } else {
                                            setSubmission(currentSubs.filter(id => id !== opt.id));
                                        }
                                    }}
                                    disabled={!!result}
                                />
                                 <span className="ml-3">{opt.text}</span>
                            </label>
                        ))}
                    </div>
                )}

                {!result && (
                    <button type="submit" className="btn btn-primary mt-4" disabled={submitting || !submission}>
                        {submitting ? <LoadingSpinner size="sm"/> : 'Submit Answer'}
                    </button>
                )}
            </form>
            {error && <div className="text-error mt-2">{error}</div>}
            {renderResult()}
        </div>
    );
};


const CourseViewerPage = () => {
    const { courseId } = useParams();
    const { user } = useContext(AuthContext);
    const [course, setCourse] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [submissionResults, setSubmissionResults] = useState({});

    useEffect(() => {
        const fetchCourse = async () => {
            if (!user?.token || !courseId) return setLoading(false);
            try {
                setLoading(true);
                const response = await fetch(`${API_URL}/courses/${courseId}`, {
                    headers: { 'Authorization': `Bearer ${user.token}` },
                });
                if (!response.ok) throw new Error('Failed to fetch course details.');
                const data = await response.json();
                setCourse(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchCourse();
    }, [courseId, user]);
    
    const handleTaskSubmit = (taskId, result) => {
        setSubmissionResults(prev => ({ ...prev, [taskId]: result }));
    };

    if (loading) return <div className="flex justify-center items-center h-screen"><LoadingSpinner /></div>;
    if (error) return <div className="text-center text-error p-4">{error}</div>;
    if (!course) return <div className="text-center p-4">Course not found.</div>;

    return (
        <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
            <div className="mb-6">
                <Link to="/employee/dashboard" className="text-primary hover:underline">&larr; Back to Dashboard</Link>
            </div>
            <header className="mb-8">
                <h1 className="text-4xl font-extrabold mb-2 text-secondary-dark">{course.title}</h1>
                <p className="text-lg text-gray-600">{course.description}</p>
            </header>
            
            <main className="space-y-8">
                {course.items && course.items.map((item, index) => (
                    <div key={item.id}>
                        <div className="flex items-center gap-4 mb-2">
                           <span className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white font-bold">{index + 1}</span>
                           <span className="text-sm font-semibold uppercase tracking-wider text-gray-500">{item.item_type}</span>
                        </div>
                        {item.item_type === 'lesson' && <LessonViewer item={item} />}
                        {item.item_type === 'task' && <TaskViewer item={item} user={user} onTaskSubmit={handleTaskSubmit} />}
                    </div>
                ))}
            </main>
        </div>
    );
};

export default CourseViewerPage;