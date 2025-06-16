import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom'; // <-- ADD THIS LINE
import { AuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/Common/LoadingSpinner';

// Mock API call - replace with your real API logic
const fetchAssignedCourses = async (managerId) => {
    // Simulate API delay
    await new Promise((res) => setTimeout(res, 500));
    // Example data (add progress and deadline fields)
    return [
        { id: 'c1', name: 'Introduction to React', progress: 30, deadline: '2024-06-15' },
        { id: 'c3', name: 'Advanced CSS Techniques', progress: 0, deadline: '2024-07-01' },
        { id: 'c5', name: 'Project Management Basics', progress: 100, deadline: '2024-05-20' },
    ];
};

const ProgressBar = ({ progress }) => ( // <-- ADD THIS COMPONENT
    <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div
            className="bg-primary h-2.5 rounded-full"
            style={{ width: `${progress}%` }}
        ></div>
    </div>
);

const ManagerHomePage = () => {
    const { user } = useContext(AuthContext);
    const [courses, setCourses] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (user && user.role === 'manager') {
            fetchAssignedCourses(user.id).then((data) => {
                setCourses(data);
                setLoading(false);
            });
        }
    }, [user]);

    if (!user || user.role !== 'manager') {
        return <div className="p-6">Access denied.</div>;
    }

    if (loading) {
        return <div className="flex justify-center items-center h-screen"><LoadingSpinner /></div>;
    }

    return (
        <div>
            <h1 className="text-3xl font-bold text-secondary-dark mb-6">My Assigned Courses</h1>
            {courses.length === 0 ? (
                <p className="text-secondary">You have no courses assigned yet.</p>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {courses.map(course => (
                        <div key={course.id} className="bg-surface rounded-lg shadow-md p-6 flex flex-col justify-between hover:shadow-lg transition-shadow duration-200">
                            <div>
                                <h2 className="text-xl font-semibold text-secondary-dark mb-2">{course.name}</h2>
                                <p className="text-sm text-secondary mb-1">Deadline: {course.deadline}</p>
                                <div className="mt-4 mb-2">
                                     <ProgressBar progress={course.progress} />
                                     <p className="text-sm text-right text-primary font-medium mt-1">{course.progress}% Complete</p>
                                </div>
                            </div>
                            <Link
                                to={`/manager/course/${course.id}`}
                                className={`mt-4 inline-block text-center px-4 py-2 rounded-md text-white font-medium transition duration-150 ease-in-out ${course.progress === 100 ? 'bg-secondary hover:bg-secondary-dark cursor-not-allowed' : 'bg-primary hover:bg-primary-dark'}`}
                                aria-disabled={course.progress === 100}
                                onClick={(e) => course.progress === 100 && e.preventDefault()} // Prevent click if completed
                            >
                                {course.progress === 0 ? 'Start Course' : course.progress === 100 ? 'Completed' : 'Continue Course'}
                            </Link>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ManagerHomePage;