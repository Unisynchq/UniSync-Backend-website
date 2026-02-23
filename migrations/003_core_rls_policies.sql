-- Consolidate RLS policies for all core tables
-- This ensures that all tables have RLS enabled and proper policies set.

-- Enable RLS on core tables
-- Note: migrations/000_core_schema.sql may have already enabled some, but this ensures it.
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_analysis ENABLE ROW LEVEL SECURITY;

-- 1. Profiles: Users can only see and update their own profiles
-- (Assuming 'profiles' table exists and has 'id' matching auth.uid())
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" 
ON public.profiles FOR SELECT 
USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" 
ON public.profiles FOR UPDATE 
USING (auth.uid() = id);

-- 2. Forms: Users can manage their own forms
-- Using owner_id instead of user_id as per schema
DROP POLICY IF EXISTS "Users can view own forms" ON public.forms;
CREATE POLICY "Users can view own forms" 
ON public.forms FOR SELECT 
USING (auth.uid() = owner_id);

DROP POLICY IF EXISTS "Users can insert own forms" ON public.forms;
CREATE POLICY "Users can insert own forms" 
ON public.forms FOR INSERT 
WITH CHECK (auth.uid() = owner_id);

DROP POLICY IF EXISTS "Users can update own forms" ON public.forms;
CREATE POLICY "Users can update own forms" 
ON public.forms FOR UPDATE 
USING (auth.uid() = owner_id);

DROP POLICY IF EXISTS "Users can delete own forms" ON public.forms;
CREATE POLICY "Users can delete own forms" 
ON public.forms FOR DELETE 
USING (auth.uid() = owner_id);

-- Public access to published forms (for form runner)
DROP POLICY IF EXISTS "Public can view published forms" ON public.forms;
CREATE POLICY "Public can view published forms" 
ON public.forms FOR SELECT 
USING (is_published = true);

-- 3. Questions: Associated with forms owned by the user
DROP POLICY IF EXISTS "Users can manage questions of own forms" ON public.questions;
CREATE POLICY "Users can manage questions of own forms" 
ON public.questions FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM public.forms 
    WHERE public.forms.id = public.questions.form_id 
    AND public.forms.owner_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Public can view questions of published forms" ON public.questions;
CREATE POLICY "Public can view questions of published forms" 
ON public.questions FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM public.forms 
    WHERE public.forms.id = public.questions.form_id 
    AND public.forms.is_published = true
  )
);

-- 4. Responses: Form owners can view responses, anyone can submit to published forms
DROP POLICY IF EXISTS "Form owners can view responses" ON public.responses;
CREATE POLICY "Form owners can view responses" 
ON public.responses FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM public.forms 
    WHERE public.forms.id = public.responses.form_id 
    AND public.forms.owner_id = auth.uid()
  )
);

DROP POLICY IF EXISTS "Anyone can submit to published forms" ON public.responses;
CREATE POLICY "Anyone can submit to published forms" 
ON public.responses FOR INSERT 
WITH CHECK (
  EXISTS (
    SELECT 1 FROM public.forms 
    WHERE public.forms.id = public.responses.form_id 
    AND public.forms.is_published = true
  )
);

-- 5. AI Analysis: Form owners can view AI analysis
DROP POLICY IF EXISTS "Owners can view AI analysis" ON public.ai_analysis;
CREATE POLICY "Owners can view AI analysis" 
ON public.ai_analysis FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.responses r
        JOIN public.forms f ON f.id = r.form_id
        WHERE r.id = public.ai_analysis.response_id
        AND f.owner_id = auth.uid()
    )
);
