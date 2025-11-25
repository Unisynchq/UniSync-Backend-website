-- Enable Row Level Security and create policy for subscriptions table
-- Run this in your Supabase SQL editor

-- Enable RLS on subscriptions table
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anyone (anon role) to insert subscriptions
CREATE POLICY "Allow public inserts on subscriptions"
ON subscriptions
FOR INSERT
TO anon
WITH CHECK (true);

-- Create policy to allow service role to read all subscriptions
CREATE POLICY "Allow service role to read subscriptions"
ON subscriptions
FOR SELECT
TO service_role
USING (true);

