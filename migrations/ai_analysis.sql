-- Create AI Analysis table
CREATE TABLE IF NOT EXISTS public.ai_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    response_id UUID NOT NULL REFERENCES public.responses(id) ON DELETE CASCADE,
    raw_analysis JSONB,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, completed, failed
    error_log TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_ai_analysis_response_id ON public.ai_analysis(response_id);

-- Enable RLS
ALTER TABLE public.ai_analysis ENABLE ROW LEVEL SECURITY;

-- Policy: Only form owners can see AI analysis for their forms
-- This requires a join with responses and forms
CREATE POLICY "Owners can view AI analysis" ON public.ai_analysis
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.responses r
            JOIN public.forms f ON f.id = r.form_id
            WHERE r.id = ai_analysis.response_id
            AND f.owner_id = auth.uid()
        )
    );
