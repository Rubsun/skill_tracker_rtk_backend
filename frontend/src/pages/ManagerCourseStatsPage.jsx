import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

// Mock data for demonstration
const mockStats = {
    courseName: 'Introduction to React',
    completionPercent: 68,
    employees: [
        { name: 'Alice Smith', percent: 100, deadline: '2024-06-10' },
        { name: 'Bob Johnson', percent: 80, deadline: '2024-06-15' },
        { name: 'Charlie Brown', percent: 50, deadline: '2024-06-08' },
        { name: 'Diana Prince', percent: 0, deadline: '2024-06-12' },
        { name: 'Ethan Hunt', percent: 90, deadline: '2024-06-09' },
    ],
};

const ManagerCourseStatsPage = () => {
    const { courseId } = useParams();
    const [stats, setStats] = useState(null);

    useEffect(() => {
        // Replace with real API call
        setTimeout(() => setStats(mockStats), 400);
    }, [courseId]);

    if (!stats) {
        return <div className="flex justify-center items-center h-full"><span>Loading...</span></div>;
    }

    const sortedEmployees = [...stats.employees].sort(
        (a, b) => new Date(a.deadline) - new Date(b.deadline)
    );
    
    return (
        <div>
            <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
                <h1 className="text-3xl font-bold text-secondary-dark">Stats</h1>
                <Link
                    to="/manager/dashboard"
                    className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-4 rounded-md transition duration-150 ease-in-out flex items-center"
                >
                    &larr; Back to Dashboard
                </Link>
            </div>

            {/* Chart */}
            <div className="bg-surface rounded-lg shadow p-6 mb-8 flex flex-col items-center">
                <h2 className="text-xl font-semibold text-secondary-dark mb-4">Completed:</h2>
                <div className="w-full max-w-lg flex flex-col items-center">
                    <div className="relative w-60 h-60 mb-4">
                        {/* Bigger circular progress bar using SVG */}
                        <svg className="w-full h-full" viewBox="0 0 120 120">
                            <circle
                                cx="60"
                                cy="60"
                                r="54"
                                stroke="#e5e7eb"
                                strokeWidth="12"
                                fill="none"
                            />
                            <circle
                                cx="60"
                                cy="60"
                                r="54"
                                stroke="#1E90FF"
                                strokeWidth="12"
                                fill="none"
                                strokeDasharray={2 * Math.PI * 54}
                                strokeDashoffset={2 * Math.PI * 54 * (1 - stats.completionPercent / 100)}
                                strokeLinecap="round"
                                style={{ transition: 'stroke-dashoffset 0.5s' }}
                            />
                            <text
                                x="60"
                                y="72"
                                textAnchor="middle"
                                fontSize="2.5rem"
                                fill="#1E90FF"
                                fontWeight="bold"
                            >
                                {stats.completionPercent}%
                            </text>
                        </svg>
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="bg-surface rounded-lg shadow overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
<thead className="bg-gray-50">
    <tr>
        <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Employee Name</th>
        <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Completion</th>
        <th className="px-6 py-3 text-left text-xs font-medium text-secondary uppercase tracking-wider">Deadline</th>
    </tr>
                </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {sortedEmployees.map((emp, idx) => (
                            <tr key={idx} className="hover:bg-gray-50 transition-colors duration-150">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-dark">{emp.name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary">
                                    <div className="flex items-center">
                                        <div className="w-32 bg-gray-200 rounded-full h-2.5 mr-3">
                                            <div
                                                className="bg-primary h-2.5 rounded-full"
                                                style={{ width: `${emp.percent}%` }}
                                            ></div>
                                        </div>
                                        <span className="ml-2 font-semibold text-primary">{emp.percent}%</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-dark">
                                    {emp.deadline}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ManagerCourseStatsPage;