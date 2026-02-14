-- Enable RLS on core tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE forms ENABLE ROW LEVEL SECURITY;
ALTER TABLE questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE responses ENABLE ROW LEVEL SECURITY;

-- 1. Profiles: Users can only see and update their own profiles
CREATE POLICY "Users can view own profile" 
ON profiles FOR SELECT 
USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
ON profiles FOR UPDATE 
USING (auth.uid() = id);

-- 2. Forms: Users can manage their own forms
CREATE POLICY "Users can view own forms" 
ON forms FOR SELECT 
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own forms" 
ON forms FOR INSERT 
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own forms" 
ON forms FOR UPDATE 
USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own forms" 
ON forms FOR DELETE 
USING (auth.uid() = user_id);

-- Public access to published forms (for form runner)
CREATE POLICY "Public can view published forms" 
ON forms FOR SELECT 
USING (is_published = true);

-- 3. Questions: Associated with forms owned by the user
CREATE POLICY "Users can manage questions of own forms" 
ON questions FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM forms 
    WHERE forms.id = questions.form_id 
    AND forms.user_id = auth.uid()
  )
);

CREATE POLICY "Public can view questions of published forms" 
ON questions FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM forms 
    WHERE forms.id = questions.form_id 
    AND forms.is_published = true
  )
);

-- 4. Responses: Form owners can view responses, anyone can submit to published forms
CREATE POLICY "Form owners can view responses" 
ON responses FOR SELECT 
USING (
  EXISTS (
    SELECT 1 FROM forms 
    WHERE forms.id = responses.form_id 
    AND forms.user_id = auth.uid()
  )
);

CREATE POLICY "Anyone can submit to published forms" 
ON responses FOR INSERT 
WITH CHECK (
  EXISTS (
    SELECT 1 FROM forms 
    WHERE forms.id = responses.form_id 
    AND forms.is_published = true
  )
);
