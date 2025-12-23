import React, { useState, useEffect } from 'react';
import api from './api';
import { LogOut, Plus, CheckCircle, Clock, AlertTriangle, ChevronLeft, ChevronRight, Layout, Edit, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const App = () => {
  const [token, setToken] = useState(() => {
    const saved = localStorage.getItem('token');
    return saved && saved !== 'null' && saved !== 'undefined' ? saved : null;
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }, [token]);

  const handleLogout = () => {
    setToken(null);
  };

  return (
    <div className="min-h-screen">
      <AnimatePresence mode="wait">
        {!token ? (
          <AuthView key="auth" setToken={setToken} />
        ) : (
          <Dashboard key="dashboard" onLogout={handleLogout} />
        )}
      </AnimatePresence>
    </div>
  );
};

const AuthView = ({ setToken }) => {
  const [view, setView] = useState('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      if (view === 'login') {
        const res = await api.post('/auth/login', { email, password });
        const newToken = res.data.access_token;
        if (newToken) {
          localStorage.setItem('token', newToken);
          setToken(newToken);
        } else {
          setError('Invalid login response');
        }
      } else {
        await api.post('/auth/register', { email, password });
        alert('Registration successful! Please login.');
        setView('login');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.05 }}
      className="flex items-center justify-center min-h-screen p-4"
    >
      <div className="glass-container w-full max-w-[450px] p-10 md:p-14 text-center">
        <h1 className="text-4xl font-black mb-12 text-white">{view === 'login' ? 'Login' : 'Register'}</h1>

        {error && (
          <div className="bg-red-500/20 text-red-200 p-3 rounded-lg text-sm mb-6 border border-red-500/30">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="text-left">
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              className="input-underline"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              className="input-underline"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="checkbox-group">
            <label>
              <input type="checkbox" defaultChecked className="accent-white" /> Remember Me
            </label>
            <button type="button" className="link-btn">Forget Password</button>
          </div>

          <button type="submit" className="btn-login" disabled={loading}>
            {loading ? 'Processing...' : (view === 'login' ? 'Log in' : 'Create Account')}
          </button>
        </form>

        <p className="mt-8 text-center text-white/50 text-sm">
          {view === 'login' ? "Don't have an account? " : "Already have an account? "}
          <button
            onClick={() => setView(view === 'login' ? 'register' : 'login')}
            className="text-white font-bold hover:underline"
          >
            {view === 'login' ? 'Register' : 'Login'}
          </button>
        </p>
      </div>
    </motion.div>
  );
};

const Dashboard = ({ onLogout }) => {
  const [tasks, setTasks] = useState([]);
  const [stats, setStats] = useState({ total_tasks: 0, pending_tasks: 0, completed_tasks: 0 });
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  const limit = 6;

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [taskRes, statRes] = await Promise.all([
          api.get(`/tasks?page=${page}&limit=${limit}`),
          api.get('/admin/stats')
        ]);
        setTasks(taskRes.data.tasks || []);
        setStats(statRes.data || { total_tasks: 0, pending_tasks: 0, completed_tasks: 0 });
        setTotalPages(Math.ceil((taskRes.data.total || 0) / limit));
      } catch (err) {
        console.error("Dashboard Fetch Error:", err);
        if (err.response?.status === 401) onLogout();
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [page, onLogout]);

  const handleDelete = async (id) => {
    if (!id || !confirm('Are you sure?')) return;
    try {
      await api.delete(`/tasks/${id}`);
      // Refresh current page
      const taskRes = await api.get(`/tasks?page=${page}&limit=${limit}`);
      setTasks(taskRes.data.tasks || []);
      setTotalPages(Math.ceil((taskRes.data.total || 0) / limit));
      // Refresh stats
      const statRes = await api.get('/admin/stats');
      setStats(statRes.data || stats);
    } catch (err) {
      alert('Action failed');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <header className="flex justify-between items-center mb-12">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 glass-container flex items-center justify-center text-white">
            <Layout size={24} />
          </div>
          <h2 className="text-3xl font-black text-white">Workspace</h2>
        </div>
        <div className="flex gap-4">
          <button onClick={() => { setEditingTask(null); setShowModal(true); }} className="btn-login px-8 !py-2 !mt-0 !w-auto text-sm">
            <Plus size={18} /> New Task
          </button>
          <button onClick={onLogout} className="glass-container px-5 py-2 flex items-center gap-2 hover:bg-white/10 transition text-sm font-bold">
            <LogOut size={16} /> Sign Out
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <StatCard title="Total" value={stats.total_tasks} icon={<Layout size={20} />} />
        <StatCard title="Doing" value={stats.pending_tasks} icon={<Clock size={20} />} />
        <StatCard title="Done" value={stats.completed_tasks} icon={<CheckCircle size={20} />} />
      </div>

      <div className="relative min-h-[300px]">
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-white"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={() => { setEditingTask(task); setShowModal(true); }}
                onDelete={() => handleDelete(task.id)}
              />
            ))}
          </div>
        )}
        {!loading && tasks.length === 0 && (
          <div className="text-center py-20 bg-white/5 rounded-3xl border border-white/5">
            <p className="text-white/30 text-lg">Your workspace is clean. Create a task! ✨</p>
          </div>
        )}
      </div>

      {!loading && totalPages > 1 && (
        <div className="mt-12 flex justify-center items-center gap-8">
          <button
            disabled={page === 1}
            onClick={() => setPage(p => p - 1)}
            className="glass-container p-3 disabled:opacity-10 hover:bg-white/10 transition"
          >
            <ChevronLeft size={20} />
          </button>
          <span className="text-xs font-black text-white/40 uppercase tracking-widest">{page} / {totalPages}</span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage(p => p + 1)}
            className="glass-container p-3 disabled:opacity-10 hover:bg-white/10 transition"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      )}

      {showModal && (
        <TaskModal
          task={editingTask}
          onClose={() => setShowModal(false)}
          onSuccess={() => { setPage(1); setShowModal(false); }}
        />
      )}
    </div>
  );
};

const StatCard = ({ title, value, icon }) => (
  <div className="glass-container p-6 bg-white/5 flex items-center gap-5">
    <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center text-white">
      {icon}
    </div>
    <div>
      <p className="text-[10px] font-black text-white/40 uppercase tracking-[2px] mb-1">{title}</p>
      <p className="text-3xl font-black text-white">{value}</p>
    </div>
  </div>
);

const TaskCard = ({ task, onEdit, onDelete }) => {
  const formatDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return isNaN(date.getTime()) ? 'Recently' : date.toLocaleDateString();
    } catch (e) {
      return 'Recently';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="task-card flex flex-col h-full"
    >
      <div className="task-card-header">
        <span className={`tag tag-priority-${task.priority || 'medium'}`}>
          {task.priority || 'Medium'}
        </span>
        <div className="flex gap-1">
          <button onClick={onEdit} className="p-2 hover:bg-white/10 rounded-lg text-white/40 hover:text-white transition">
            <Edit size={14} />
          </button>
          <button onClick={onDelete} className="p-2 hover:bg-white/10 rounded-lg text-white/40 hover:text-red-400 transition">
            <Trash2 size={14} />
          </button>
        </div>
      </div>
      <h3 className="task-title mb-2">{task.title || 'Untitled Task'}</h3>
      <p className="task-description flex-grow">
        {task.description || 'No description provided.'}
      </p>
      <div className="flex justify-between items-center mt-6 pt-4 border-t border-white/5">
        <span className="tag tag-status">{(task.status || 'pending').replace('_', ' ')}</span>
        <span className="text-[10px] text-white/20 font-black tracking-widest uppercase">
          {formatDate(task.created_at)}
        </span>
      </div>
    </motion.div>
  );
};

const TaskModal = ({ task, onClose, onSuccess }) => {
  const [formData, setFormData] = useState(task || {
    title: '',
    description: '',
    status: 'pending',
    priority: 'medium'
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (task) {
        await api.put(`/tasks/${task.id}`, formData);
      } else {
        await api.post('/tasks', formData);
      }
      onSuccess();
    } catch (err) {
      alert('Error updating task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xl">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="glass-container w-full max-w-lg p-12 bg-indigo-950/20"
      >
        <h3 className="text-3xl font-black text-white mb-10">{task ? 'Edit' : 'New'} Task</h3>
        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="input-group !mb-0">
            <label>Title</label>
            <input
              type="text"
              className="input-underline"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              required
              autoFocus
            />
          </div>
          <div className="input-group !mb-0">
            <label>Description</label>
            <textarea
              className="input-underline min-h-[100px] resize-none"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-10">
            <div className="input-group !mb-0">
              <label>Status</label>
              <select
                className="input-underline !bg-[#1e1b4b]"
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              >
                <option value="pending">Pending</option>
                <option value="in_progress">Ongoing</option>
                <option value="completed">Done</option>
              </select>
            </div>
            <div className="input-group !mb-0">
              <label>Priority</label>
              <select
                className="input-underline !bg-[#1e1b4b]"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
          </div>
          <div className="flex gap-6 pt-6">
            <button type="button" onClick={onClose} className="link-btn flex-1 py-4 text-white/30 hover:text-white transition">Cancel</button>
            <button type="submit" className="btn-login !mt-0 flex-1 !py-4 shadow-2xl" disabled={loading}>
              {loading ? 'Saving...' : 'Save Task'}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
};

export default App;
