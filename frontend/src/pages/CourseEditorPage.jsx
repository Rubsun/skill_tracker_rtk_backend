import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import { AuthContext } from '../contexts/AuthContext';
import { PlusIcon, PencilIcon, TrashIcon } from '../components/Icons'; // Assuming you have icons

const API_URL = 'http://localhost:8000/api/v1';

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


const CourseEditorPage = ({ mode }) => {
    const { courseId } = useParams();
    const navigate = useNavigate();
    const { user } = useContext(AuthContext);
    const isEditMode = mode === 'edit';

    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [items, setItems] = useState([]);
    
    const [currentItem, setCurrentItem] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [itemTypeToCreate, setItemTypeToCreate] = useState(null); // 'lesson' or 'task'
    const [taskTypeToCreate, setTaskTypeToCreate] = useState(null); // 'long_answer', etc.

    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isEditMode && courseId) {
            // TODO: Fetch existing course data and populate state
        }
    }, [courseId, isEditMode]);

    const openModal = (item = null) => {
        if (item) {
            setCurrentItem({ ...item });
        }
        setIsModalOpen(true);
    };

    const handleSelectItemType = (type) => {
        setItemTypeToCreate(type);
        if (type === 'lesson') {
            setCurrentItem({ id: null, item_type: 'lesson', title: '', content: '' });
        } else {
            // Further selection needed for task type
        }
    };
    
    const handleSelectTaskType = (type) => {
        setTaskTypeToCreate(type);
        setCurrentItem({ 
            id: null, 
            item_type: 'task', 
            task_type: type,
            title: '', 
            question: '',
            ...(type !== 'long_answer' && { options: [] })
        });
    };

    const closeModal = () => {
        setIsModalOpen(false);
        setCurrentItem(null);
        setItemTypeToCreate(null);
        setTaskTypeToCreate(null);
    };

    const handleSaveItem = () => {
        if (!currentItem?.title) return;
        
        if (currentItem.id) { // Editing existing
            setItems(items.map(i => i.id === currentItem.id ? currentItem : i));
        } else { // Adding new
            setItems([...items, { ...currentItem, id: `temp-${Date.now()}` }]);
        }
        closeModal();
    };

    const handleDeleteItem = (itemId) => {
        setItems(items.filter(i => i.id !== itemId));
    };

    const handleSubmitCourse = async (e) => {
        e.preventDefault();
        if (!user?.token) return setError("Authentication required.");
        if (items.length === 0) return setError("A course must have at least one lesson or task.");

        setSaving(true);
        setError('');

        const courseData = {
            title,
            description,
            items: items.map(({ id, ...rest }) => rest), // Remove temp frontend ID
        };
        
        try {
            const response = await fetch(`${API_URL}/courses/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${user.token}`,
                },
                body: JSON.stringify(courseData),
            });

            if (!response.ok) throw new Error((await response.json()).detail || 'Failed to create course');
            
            navigate('/manager/dashboard');
        } catch (err) {
            setError(err.message);
        } finally {
            setSaving(false);
        }
    };
    
    // --- Render Logic ---
    const renderModalContent = () => {
        if (!currentItem) {
            if (!itemTypeToCreate) {
                return ( // Step 1: Choose Lesson or Task
                    <div>
                        <h3 className="text-lg font-bold mb-4">What would you like to add?</h3>
                        <div className="flex gap-4">
                           <button type="button" onClick={() => handleSelectItemType('lesson')} className="btn btn-secondary w-full">Lesson</button>
                           <button type="button" onClick={() => handleSelectItemType('task')} className="btn btn-accent w-full">Task</button>
                        </div>
                    </div>
                );
            }
            if (itemTypeToCreate === 'task' && !taskTypeToCreate) {
                 return ( // Step 2: Choose Task Type
                    <div>
                        <h3 className="text-lg font-bold mb-4">Select Task Type</h3>
                        <div className="grid grid-cols-1 gap-3">
                            <button type="button" onClick={() => handleSelectTaskType('single_choice')} className="btn btn-outline">Single Choice</button>
                            <button type="button" onClick={() => handleSelectTaskType('multiple_choice')} className="btn btn-outline">Multiple Choice</button>
                            <button type="button" onClick={() => handleSelectTaskType('long_answer')} className="btn btn-outline">Long Answer</button>
                        </div>
                         <button type="button" onClick={() => setItemTypeToCreate(null)} className="btn btn-ghost mt-4">Back</button>
                    </div>
                );
            }
        }
        
        // Step 3: Show the form for the selected item
        return (
            <div>
                 <h3 className="text-lg font-bold mb-4">{currentItem.id ? 'Edit' : 'Add'} {currentItem.item_type}</h3>
                 <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
                    {currentItem.item_type === 'lesson' && <LessonForm item={currentItem} setItem={setCurrentItem} />}
                    {currentItem.item_type === 'task' && <TaskForm item={currentItem} setItem={setCurrentItem} />}
                 </div>
                <div className="flex justify-end gap-4 mt-6 pt-4 border-t">
                    <button type="button" onClick={closeModal} className="btn btn-ghost">Cancel</button>
                    <button type="button" onClick={handleSaveItem} className="btn btn-primary">Save Item</button>
                </div>
            </div>
        );
    }
    
    return (
        <div className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
            <h1 className="text-2xl md:text-3xl font-bold text-secondary-dark mb-6">
                {isEditMode ? 'Edit Course' : 'Create New Course'}
            </h1>
            
            {error && <div className="bg-error-light text-error-dark p-3 rounded-md mb-4">{error}</div>}
            
            <form onSubmit={handleSubmitCourse} className="bg-surface p-6 rounded-lg shadow-md space-y-6">
                 <div>
                    <label htmlFor="courseTitle" className="block text-sm font-medium text-gray-700 mb-1">Course Title</label>
                    <input type="text" id="courseTitle" value={title} onChange={(e) => setTitle(e.target.value)} required className="w-full input" />
                </div>
                <div>
                    <label htmlFor="courseDescription" className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <textarea id="courseDescription" value={description} onChange={(e) => setDescription(e.target.value)} required rows="4" className="w-full input" />
                </div>
                
                <div className="border-t pt-6">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold text-secondary-dark">Course Content</h2>
                         <button type="button" onClick={() => openModal()} className="btn btn-secondary">
                            <PlusIcon /> Add Item
                        </button>
                    </div>
                    {items.length > 0 ? (
                        <ul className="space-y-2">
                            {items.map((item) => (
                                <ItemRenderer key={item.id} item={item} onEdit={openModal} onDelete={handleDeleteItem} />
                            ))}
                        </ul>
                    ) : (
                        <p className="text-center text-gray-500 py-6 bg-gray-50 rounded-md">This course has no content yet. Click "Add Item" to get started.</p>
                    )}
                </div>

                <div className="flex items-center justify-end gap-4 pt-6 border-t">
                    <button type="button" onClick={() => navigate('/manager/dashboard')} className="btn btn-ghost" disabled={saving}>Cancel</button>
                    <button type="submit" className="btn btn-primary" disabled={saving}>
                        {saving ? <LoadingSpinner size="sm" /> : 'Save Course'}
                    </button>
                </div>
            </form>

            {isModalOpen && (
                 <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-2xl">
                        {renderModalContent()}
                    </div>
                </div>
            )}
        </div>
    );
};

export default CourseEditorPage;