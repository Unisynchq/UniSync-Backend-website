-- UniSync Consolidated Database Schema
-- Consolidates all migrations into a single file for Supabase setup.

-- 0. Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table (Mirrors auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Forms Table
CREATE TABLE IF NOT EXISTS public.forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    is_published BOOLEAN DEFAULT FALSE,
    is_ai_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Questions Table
CREATE TABLE IF NOT EXISTS public.questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES public.forms(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    type TEXT NOT NULL, -- text, number, select, multiselect, date
    order_index INTEGER NOT NULL,
    options JSONB, -- For select/multiselect choices
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Responses Table
CREATE TABLE IF NOT EXISTS public.responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_id UUID NOT NULL REFERENCES public.forms(id) ON DELETE CASCADE,
    answers JSONB NOT NULL, -- {question_id: answer_value}
    metadata JSONB, -- IP, User Agent, etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. AI Analysis Table
CREATE TABLE IF NOT EXISTS public.ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    response_id UUID NOT NULL REFERENCES public.responses(id) ON DELETE CASCADE,
    raw_analysis JSONB,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, completed, failed
    error_log TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Feedback Items (Simplified for Analytics & Inbox)
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

-- 7. Action Tasks (Kanban Board)
CREATE TABLE IF NOT EXISTS public.action_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo', -- 'todo', 'inProgress', 'completed'
    context TEXT,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Trend Data Points
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

-- 9. Category Insights
CREATE TABLE IF NOT EXISTS public.category_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_name TEXT NOT NULL,
    insights JSONB DEFAULT '[]'::jsonb,
    themes JSONB DEFAULT '[]'::jsonb,
    actionable JSONB DEFAULT '[]'::jsonb,
    date_generated TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(category_name)
);

-- 10. Subscriptions Table
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    source TEXT DEFAULT 'landing_hero',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'unsubscribed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_forms_owner_id ON public.forms(owner_id);
CREATE INDEX IF NOT EXISTS idx_forms_slug ON public.forms(slug);
CREATE INDEX IF NOT EXISTS idx_questions_form_id ON public.questions(form_id);
CREATE INDEX IF NOT EXISTS idx_responses_form_id ON public.responses(form_id);
CREATE INDEX IF NOT EXISTS idx_ai_analysis_response_id ON public.ai_analysis(response_id);
CREATE INDEX IF NOT EXISTS idx_feedback_items_sem_type ON public.feedback_items(sem_type);
CREATE INDEX IF NOT EXISTS idx_feedback_items_status ON public.feedback_items(status);
CREATE INDEX IF NOT EXISTS idx_action_tasks_status ON public.action_tasks(status);
CREATE INDEX IF NOT EXISTS idx_trend_data_points_date ON public.trend_data_points(date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_email ON public.subscriptions(email);

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.action_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.trend_data_points ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.category_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;

-- Policies
-- Profiles: Users can view/update own
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Forms: Owners manage, Public views published
CREATE POLICY "Users can manage own forms" ON public.forms FOR ALL USING (auth.uid() = owner_id);
CREATE POLICY "Public can view published forms" ON public.forms FOR SELECT USING (is_published = true);

-- Questions: Associated with owner's forms
CREATE POLICY "Users can manage questions" ON public.questions FOR ALL USING (EXISTS (SELECT 1 FROM public.forms WHERE id = form_id AND owner_id = auth.uid()));
CREATE POLICY "Public view questions" ON public.questions FOR SELECT USING (EXISTS (SELECT 1 FROM public.forms WHERE id = form_id AND is_published = true));

-- Responses: Anyone can submit, Owners view
CREATE POLICY "Anyone can submit responses" ON public.responses FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM public.forms WHERE id = form_id AND is_published = true));
CREATE POLICY "Owners view responses" ON public.responses FOR SELECT USING (EXISTS (SELECT 1 FROM public.forms WHERE id = form_id AND owner_id = auth.uid()));

-- Feedback Items & Tasks: Authenticated users only
CREATE POLICY "Authenticated users manage feedback" ON public.feedback_items FOR ALL USING (auth.role() = 'authenticated');
CREATE POLICY "Authenticated users manage tasks" ON public.action_tasks FOR ALL USING (auth.role() = 'authenticated');
