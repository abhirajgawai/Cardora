'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Plus, Pencil, Trash2, Check, X, Loader2 } from 'lucide-react';
import {
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
  type Category,
} from '@/features/settings/api/categoriesApi';

export default function CategorySettings() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newName, setNewName] = useState('');
  const [newIcon, setNewIcon] = useState('');
  const [creating, setCreating] = useState(false);

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  const [editIcon, setEditIcon] = useState('');
  const [savingId, setSavingId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getCategories();
        setCategories(data);
      } catch {
        setError('Failed to load categories');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name || creating) return;
    setCreating(true);
    setError(null);
    try {
      const created = await createCategory({
        name,
        icon: newIcon.trim() || null,
      });
      setCategories((prev) => [...prev, created]);
      setNewName('');
      setNewIcon('');
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(message || 'Failed to create category');
    } finally {
      setCreating(false);
    }
  };

  const startEdit = (category: Category) => {
    setEditingId(category.id);
    setEditName(category.name);
    setEditIcon(category.icon ?? '');
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName('');
    setEditIcon('');
  };

  const handleSave = async (id: string) => {
    if (savingId) return;
    setSavingId(id);
    setError(null);
    try {
      const updated = await updateCategory(id, {
        name: editName.trim(),
        icon: editIcon.trim() || null,
      });
      setCategories((prev) => prev.map((c) => (c.id === id ? updated : c)));
      cancelEdit();
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(message || 'Failed to update category');
    } finally {
      setSavingId(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (deletingId) return;
    setDeletingId(id);
    setError(null);
    try {
      await deleteCategory(id);
      setCategories((prev) => prev.filter((c) => c.id !== id));
    } catch (err) {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(message || 'Failed to delete category');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-4"></div>
          <p className="text-muted-foreground">Loading categories...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fintech-card p-8"
      >
        <h2 className="text-2xl font-bold text-foreground mb-2">Categories</h2>
        <p className="text-muted-foreground mb-6">
          Create custom categories to organize your spending. System categories cannot be changed.
        </p>

        {error && (
          <div className="mb-4 rounded-md bg-destructive/10 text-destructive px-4 py-2 text-sm">
            {error}
          </div>
        )}

        {/* Create */}
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="New category name"
            maxLength={100}
            className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
          <input
            type="text"
            value={newIcon}
            onChange={(e) => setNewIcon(e.target.value)}
            placeholder="Icon"
            maxLength={10}
            className="w-20 rounded-md border border-input bg-background px-3 py-2 text-sm text-center"
          />
          <button
            onClick={handleCreate}
            disabled={!newName.trim() || creating}
            className="inline-flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
          >
            {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Add
          </button>
        </div>

        {/* List */}
        <ul className="divide-y divide-border">
          {categories.map((category) => (
            <li key={category.id} className="flex items-center gap-3 py-3">
              {editingId === category.id ? (
                <>
                  <input
                    type="text"
                    value={editIcon}
                    onChange={(e) => setEditIcon(e.target.value)}
                    maxLength={10}
                    className="w-16 rounded-md border border-input bg-background px-2 py-1 text-sm text-center"
                  />
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    maxLength={100}
                    className="flex-1 rounded-md border border-input bg-background px-2 py-1 text-sm"
                  />
                  <button
                    onClick={() => handleSave(category.id)}
                    disabled={savingId === category.id}
                    className="p-2 text-green-600 hover:bg-muted rounded-md disabled:opacity-50"
                    aria-label="Save"
                  >
                    {savingId === category.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Check className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="p-2 text-muted-foreground hover:bg-muted rounded-md"
                    aria-label="Cancel"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              ) : (
                <>
                  <span className="w-8 text-center">{category.icon ?? '🏷️'}</span>
                  <span className="flex-1 text-sm text-foreground">
                    {category.name}
                    {!category.is_custom && (
                      <span className="ml-2 text-xs text-muted-foreground">(system)</span>
                    )}
                  </span>
                  {category.is_custom && (
                    <>
                      <button
                        onClick={() => startEdit(category)}
                        className="p-2 text-muted-foreground hover:bg-muted rounded-md"
                        aria-label={`Edit ${category.name}`}
                      >
                        <Pencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(category.id)}
                        disabled={deletingId === category.id}
                        className="p-2 text-destructive hover:bg-muted rounded-md disabled:opacity-50"
                        aria-label={`Delete ${category.name}`}
                      >
                        {deletingId === category.id ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </>
                  )}
                </>
              )}
            </li>
          ))}
        </ul>
      </motion.div>
    </div>
  );
}
