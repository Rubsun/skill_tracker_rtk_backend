import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import LoadingSpinner from '../components/Common/LoadingSpinner';

// --- Mock Data & API Calls ---
const mockCourseDetails = {
    c1: { id: 'c1', name: 'Introduction to React' },
    c2: { id: 'c2', name: 'Advanced TypeScript' },
    c3: { id: 'c3', name: 'Advanced CSS Techniques' },
    c4: { id: 'c4', name: 'Docker Fundamentals' },
    c5: { id: 'c5', name: 'Project Management Basics' },
};

const mockEmployees = [
    { id: 'e1', name: 'Alice Smith' },
    { id: 'e2', name: 'Bob Johnson' },
    { id: 'e3', name: 'Charlie Brown' },
    { id: 'e4', name: 'Diana Prince' },
    { id: 'e5', name: 'Ethan Hunt' },
];

// Simulate fetching data
const fetchCourseDetails = async (courseId) => {
    console.log("Fetching course details for assignment:", courseId);
    await new Promise(resolve => setTimeout(resolve, 200));
    if (mockCourseDetails[courseId]) {
        return mockCourseDetails[courseId];
    } else {
        throw new Error("Course not found");
    }
};

const fetchAllEmployees = async () => {
    console.log("Fetching all employees");
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockEmployees;
};

// Simulate fetching current assignments for THIS course
const getCourseAssignments = async (courseId) => {
    console.log("Fetching assignments for course:", courseId);
    await new Promise(resolve => setTimeout(resolve, 250));
    // Mock: Let's say Alice and Charlie are already assigned to course c1
    if (courseId === 'c1') {
        return ['e1', 'e3'];
    }
    return []; // No assignments for other courses by default
};

// Simulate assigning the course
const assignCourseToEmployees = async (courseId, employeeIds, deadline) => {
    console.log("Assigning course:", courseId, "to employees:", employeeIds, "with deadline:", deadline);
    await new Promise(resolve => setTimeout(resolve, 600));
    // In a real app, handle potential errors here
    console.log("Assignment successful (mock)");
    return true; // Simulate success
};


const CourseAssignmentPage = () => {
    const { courseId } = useParams();
    const navigate = useNavigate();

    const [courseName, setCourseName] = useState('');
    const [employees, setEmployees] = useState([]);
    const [assignedEmployees, setAssignedEmployees] = useState(new Set()); // IDs of already assigned
    const [selectedEmployees, setSelectedEmployees] = useState(new Set()); // IDs selected in UI
    const [deadline, setDeadline] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    // Fetch initial data
    useEffect(() => {
        const loadData = async () => {
            setLoading(true);
            setError('');
            setSuccessMessage('');
            try {
                const [course, employeeList, assignedIds] = await Promise.all([
                    fetchCourseDetails(courseId),
                    fetchAllEmployees(),
                    getCourseAssignments(courseId)
                ]);
                setCourseName(course.name);
                setEmployees(employeeList);
                const initialAssigned = new Set(assignedIds);
                setAssignedEmployees(initialAssigned);
                setSelectedEmployees(initialAssigned); // Start selection with currently assigned
            } catch (err) {
                console.error("Error loading assignment data:", err);
                setError('Failed to load data. Please try again.');
                setCourseName('');
                setEmployees([]);
                setAssignedEmployees(new Set());
                setSelectedEmployees(new Set());
            } finally {
                setLoading(false);
            }
        };
        loadData();
    }, [courseId]);

    const handleCheckboxChange = (employeeId) => {
        setSelectedEmployees(prevSelected => {
            const newSelected = new Set(prevSelected);
            if (newSelected.has(employeeId)) {
                newSelected.delete(employeeId);
            } else {
                newSelected.add(employeeId);
            }
            return newSelected;
        });
        // Clear success message on interaction
        setSuccessMessage('');
    };

    const handleAssignCourse = async (e) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        setSuccessMessage('');

        // Determine who needs to be assigned (newly selected)
        // For simplicity, this mock will just send all currently selected ones.
        // A real app might differentiate between new/existing or handle unassignments.
        const employeeIdsToAssign = Array.from(selectedEmployees);

        if (employeeIdsToAssign.length === 0) {
            setError("Please select at least one employee to assign.");
            setSaving(false);
            return;
        }
        if (!deadline) {
            setError("Please set a deadline for the assignment.");
            setSaving(false);
            return;
        }

        try {
            const success = await assignCourseToEmployees(courseId, employeeIdsToAssign, deadline);
            if (success) {
                setSuccessMessage(`Course successfully assigned to ${employeeIdsToAssign.length} employee(s).`);
                // Update the "assigned" state to reflect the latest successful assignment
                setAssignedEmployees(new Set(selectedEmployees));
                // Optionally navigate back or stay
                // navigate('/manager/dashboard');
            } else {
                setError('Failed to assign the course. Please try again.');
            }
        } catch (err) {
            console.error("Error assigning course:", err);
            setError('An error occurred during assignment. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <div className="flex justify-center items-center h-full"><LoadingSpinner /></div>;
    }

    if (error && !courseName) { // Critical error preventing display
        return <div className="text-center text-error p-4">{error}</div>;
    }

    return (
        <div className="max-w-4xl mx-auto p-4">
            <div className="flex justify-between items-center mb-4">
                <h1 className="text-2xl font-bold text-secondary-dark">
                    Assign Course: <span className="text-primary">{courseName || 'Loading...'}</span>
                </h1>
                <Link
                    to="/manager/dashboard"
                    className="text-sm text-primary hover:underline"
                >
                    &larr; Back to Dashboard
                </Link>
            </div>

            {error && <div className="bg-error/10 text-error text-sm p-3 rounded mb-4">{error}</div>}
            {successMessage && <div className="bg-success/10 text-success text-sm p-3 rounded mb-4">{successMessage}</div>}

            <form onSubmit={handleAssignCourse}>
                <div className="bg-surface p-6 rounded-lg shadow-md">
                    <div className="mb-6">
                        <label htmlFor="deadline" className="block text-sm font-medium text-secondary mb-1">
                            Set Deadline for Assignment
                        </label>
                        <input
                            type="date"
                            id="deadline"
                            value={deadline}
                            onChange={(e) => { setDeadline(e.target.value); setSuccessMessage(''); setError(''); }}
                            required
                            className="w-full md:w-1/2 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-light focus:border-transparent"
                            min={new Date().toISOString().split("T")[0]} // Prevent past dates
                        />
                    </div>

                    <h2 className="text-lg font-semibold text-secondary-dark mb-3">Select Employees</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 max-h-96 overflow-y-auto border p-4 rounded-md bg-gray-50">
                        {employees.length > 0 ? (
                            employees.map((employee) => (
                                <div key={employee.id} className="flex items-center">
                                    <input
                                        type="checkbox"
                                        id={`employee-${employee.id}`}
                                        checked={selectedEmployees.has(employee.id)}
                                        onChange={() => handleCheckboxChange(employee.id)}
                                        className="h-4 w-4 text-primary border-gray-300 rounded focus:ring-primary"
                                    />
                                    <label htmlFor={`employee-${employee.id}`} className="ml-2 block text-sm text-secondary-dark">
                                        {employee.name}
                                        {assignedEmployees.has(employee.id) && <span className="text-xs text-green-600 ml-1">(Already Assigned)</span>}
                                    </label>
                                </div>
                            ))
                        ) : (
                            <p className="text-secondary col-span-full">No employees found.</p>
                        )}
                    </div>

                    <div className="mt-6 text-right">
                        <button
                            type="submit"
                            disabled={saving || loading}
                            className="bg-primary hover:bg-primary-dark text-white font-bold py-2 px-6 rounded-md focus:outline-none focus:shadow-outline transition duration-150 ease-in-out flex items-center justify-center min-w-[120px] disabled:opacity-50"
                        >
                            {saving ? <LoadingSpinner /> : 'Assign Course'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default CourseAssignmentPage;