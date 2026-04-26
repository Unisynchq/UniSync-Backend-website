-- UniSync Sync Schema for Frontend Analytics & Action Board
-- Adds tables to support Dashboard, Feedback Inbox, Trends, Insights, and Action Board.

-- 1. Feedback Items (Simplified for Analytics & Inbox)
CREATE TABLE IF NOT EXISTS public.feedback_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_name TEXT,
    user_email TEXT,
    score INTEGER NOT NULL DEFAULT 0,
    comment TEXT,
    sem_type TEXT, -- e.g., 'Positive', 'Neutral', 'Negative'
    section TEXT,
    categories JSONB DEFAULT '[]'::jsonb, -- Array of strings
    status TEXT DEFAULT 'new', -- e.g., 'new', 'reviewed', 'resolved'
    is_reviewed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Action Tasks (Kanban Board)
CREATE TABLE IF NOT EXISTS public.action_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo', -- 'todo', 'inProgress', 'completed'
    context TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Trend Data Points
CREATE TABLE IF NOT EXISTS public.trend_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    clarity_score NUMERIC(5,2) DEFAULT 0,
    engagement_score NUMERIC(5,2) DEFAULT 0,
    support_score NUMERIC(5,2) DEFAULT 0,
    org_score NUMERIC(5,2) DEFAULT 0,
    period_type TEXT NOT NULL DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Category Insights
CREATE TABLE IF NOT EXISTS public.category_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name TEXT NOT NULL,
    insights JSONB DEFAULT '[]'::jsonb,
    themes JSONB DEFAULT '[]'::jsonb,
    actionable JSONB DEFAULT '[]'::jsonb,
    date_generated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category_name)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_feedback_items_sem_type ON public.feedback_items(sem_type);
CREATE INDEX IF NOT EXISTS idx_feedback_items_status ON public.feedback_items(status);
CREATE INDEX IF NOT EXISTS idx_action_tasks_status ON public.action_tasks(status);
CREATE INDEX IF NOT EXISTS idx_trend_data_points_date ON public.trend_data_points(date);

-- Enable RLS
ALTER TABLE public.feedback_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.action_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_data_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.category_insights ENABLE ROW LEVEL SECURITY;

-- Note: Policies need to be added to allow authenticated users to read/write based on your auth model.
