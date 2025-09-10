-- JarvisX Database Schema for Supabase
-- This file contains the SQL schema for all database tables

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Profiles table - stores user information
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Conversations table - stores conversation sessions
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    summary TEXT,
    metadata JSONB DEFAULT '{}',
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table - stores individual messages in conversations
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'text' CHECK (content_type IN ('text', 'image', 'file', 'chart', 'table')),
    metadata JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Permissions table - stores user permission policies
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    capability TEXT NOT NULL CHECK (capability IN (
        'FILE_READ', 'FILE_WRITE', 'PROCESS_EXECUTION', 'NETWORK_ACCESS',
        'MODEL_TRAINING', 'SYSTEM_CONTROL', 'DATA_ACCESS', 'API_ACCESS'
    )),
    policy TEXT NOT NULL CHECK (policy IN (
        'ask-every-time', 'trusted-once', 'always-deny', 'always-allow'
    )),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by TEXT REFERENCES profiles(user_id),
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique user-capability combinations
    UNIQUE(user_id, capability)
);

-- Skills table - stores skill usage and performance metrics
CREATE TABLE IF NOT EXISTS skills (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    description TEXT,
    capabilities TEXT[],
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    is_enabled BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Skill_executions table - stores individual skill execution logs
CREATE TABLE IF NOT EXISTS skill_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    query TEXT NOT NULL,
    result_type TEXT NOT NULL,
    result_content TEXT,
    artifacts JSONB DEFAULT '[]',
    execution_time_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Files table - stores file metadata and references
CREATE TABLE IF NOT EXISTS files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT,
    file_hash TEXT NOT NULL,
    is_temporary BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Models table - stores trained ML models
CREATE TABLE IF NOT EXISTS models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    model_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    training_data_hash TEXT,
    accuracy_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    mse_score DECIMAL(10,6),
    r2_score DECIMAL(5,4),
    training_time_ms INTEGER,
    parameters JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions table - stores user session information
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
    session_token TEXT UNIQUE NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit_logs table - stores security and activity audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT REFERENCES profiles(user_id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id TEXT,
    details JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_conversations_archived ON conversations(is_archived);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_role ON messages(role);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

CREATE INDEX IF NOT EXISTS idx_permissions_user_id ON permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_permissions_capability ON permissions(capability);
CREATE INDEX IF NOT EXISTS idx_permissions_policy ON permissions(policy);

CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
CREATE INDEX IF NOT EXISTS idx_skills_enabled ON skills(is_enabled);

CREATE INDEX IF NOT EXISTS idx_skill_executions_skill_id ON skill_executions(skill_id);
CREATE INDEX IF NOT EXISTS idx_skill_executions_user_id ON skill_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_executions_created_at ON skill_executions(created_at);

CREATE INDEX IF NOT EXISTS idx_files_user_id ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_temporary ON files(is_temporary);
CREATE INDEX IF NOT EXISTS idx_files_expires_at ON files(expires_at);

CREATE INDEX IF NOT EXISTS idx_models_user_id ON models(user_id);
CREATE INDEX IF NOT EXISTS idx_models_type ON models(model_type);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_permissions_updated_at BEFORE UPDATE ON permissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_models_updated_at BEFORE UPDATE ON models
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create RLS (Row Level Security) policies
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE skill_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;
ALTER TABLE models ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Profiles policy - users can only see their own profile
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own profile" ON profiles
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- Conversations policy - users can only see their own conversations
CREATE POLICY "Users can view own conversations" ON conversations
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own conversations" ON conversations
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own conversations" ON conversations
    FOR UPDATE USING (auth.uid()::text = user_id);

CREATE POLICY "Users can delete own conversations" ON conversations
    FOR DELETE USING (auth.uid()::text = user_id);

-- Messages policy - users can only see messages from their conversations
CREATE POLICY "Users can view messages from own conversations" ON messages
    FOR SELECT USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()::text
        )
    );

CREATE POLICY "Users can insert messages to own conversations" ON messages
    FOR INSERT WITH CHECK (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()::text
        )
    );

-- Permissions policy - users can only see their own permissions
CREATE POLICY "Users can view own permissions" ON permissions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can manage own permissions" ON permissions
    FOR ALL USING (auth.uid()::text = user_id);

-- Skills policy - public read, admin write
CREATE POLICY "Anyone can view skills" ON skills
    FOR SELECT USING (true);

CREATE POLICY "Only admins can modify skills" ON skills
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Skill executions policy - users can only see their own executions
CREATE POLICY "Users can view own skill executions" ON skill_executions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own skill executions" ON skill_executions
    FOR INSERT WITH CHECK (auth.uid()::text = user_id);

-- Files policy - users can only see their own files
CREATE POLICY "Users can view own files" ON files
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can manage own files" ON files
    FOR ALL USING (auth.uid()::text = user_id);

-- Models policy - users can only see their own models
CREATE POLICY "Users can view own models" ON models
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can manage own models" ON models
    FOR ALL USING (auth.uid()::text = user_id);

-- Sessions policy - users can only see their own sessions
CREATE POLICY "Users can view own sessions" ON sessions
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can manage own sessions" ON sessions
    FOR ALL USING (auth.uid()::text = user_id);

-- Audit logs policy - users can only see their own audit logs
CREATE POLICY "Users can view own audit logs" ON audit_logs
    FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "System can insert audit logs" ON audit_logs
    FOR INSERT WITH CHECK (true);

-- Insert default skills
INSERT INTO skills (name, version, description, capabilities) VALUES
('Natural Language Processing', '1.0.0', 'Text analysis, summarization, and language processing', ARRAY['summarization', 'translation', 'extraction']),
('Machine Learning', '1.0.0', 'Model training, prediction, and evaluation', ARRAY['model_training', 'prediction', 'evaluation']),
('Data Science', '1.0.0', 'Data analysis, visualization, and insights', ARRAY['data_analysis', 'visualization', 'profiling']),
('Data Engineering', '1.0.0', 'Data processing, transformation, and pipelines', ARRAY['data_processing', 'transformation', 'cleaning']),
('Analytics', '1.0.0', 'Business intelligence and reporting', ARRAY['insights', 'reporting', 'trends']),
('Automation', '1.0.0', 'Task automation and workflow creation', ARRAY['automation', 'workflows', 'scheduling']),
('Cybersecurity', '1.0.0', 'Security analysis and vulnerability assessment', ARRAY['vulnerability_scanning', 'log_analysis', 'integrity_checking']),
('System Control', '1.0.0', 'System monitoring and control', ARRAY['monitoring', 'control', 'status']),
('UI/UX Design', '1.0.0', 'Interface design and user experience', ARRAY['wireframing', 'prototyping', 'analysis']),
('Web Search', '1.0.0', 'Web scraping and information retrieval', ARRAY['scraping', 'search', 'extraction'])
ON CONFLICT (name) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW conversation_summary AS
SELECT 
    c.id,
    c.title,
    c.user_id,
    p.name as user_name,
    c.created_at,
    c.updated_at,
    COUNT(m.id) as message_count,
    MAX(m.created_at) as last_message_at
FROM conversations c
LEFT JOIN messages m ON c.id = m.conversation_id
LEFT JOIN profiles p ON c.user_id = p.user_id
GROUP BY c.id, c.title, c.user_id, p.name, c.created_at, c.updated_at;

CREATE OR REPLACE VIEW skill_performance AS
SELECT 
    s.name as skill_name,
    s.version,
    COUNT(se.id) as total_executions,
    COUNT(CASE WHEN se.success THEN 1 END) as successful_executions,
    ROUND(
        COUNT(CASE WHEN se.success THEN 1 END)::DECIMAL / COUNT(se.id)::DECIMAL * 100, 2
    ) as success_rate,
    ROUND(AVG(se.execution_time_ms), 2) as avg_execution_time_ms,
    s.last_used
FROM skills s
LEFT JOIN skill_executions se ON s.id = se.skill_id
GROUP BY s.id, s.name, s.version, s.last_used;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;

-- Create function to clean up expired temporary files
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM files 
    WHERE is_temporary = TRUE 
    AND expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM sessions 
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user statistics
CREATE OR REPLACE FUNCTION get_user_stats(user_id_param TEXT)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_conversations', COUNT(c.id),
        'total_messages', COUNT(m.id),
        'total_files', COUNT(f.id),
        'total_models', COUNT(mo.id),
        'avg_messages_per_conversation', ROUND(AVG(msg_count.count), 2),
        'most_used_skill', (
            SELECT s.name 
            FROM skill_executions se 
            JOIN skills s ON se.skill_id = s.id 
            WHERE se.user_id = user_id_param 
            GROUP BY s.id, s.name 
            ORDER BY COUNT(*) DESC 
            LIMIT 1
        )
    ) INTO result
    FROM profiles p
    LEFT JOIN conversations c ON p.user_id = c.user_id
    LEFT JOIN messages m ON c.id = m.conversation_id
    LEFT JOIN files f ON p.user_id = f.user_id
    LEFT JOIN models mo ON p.user_id = mo.user_id
    LEFT JOIN (
        SELECT conversation_id, COUNT(*) as count
        FROM messages
        GROUP BY conversation_id
    ) msg_count ON c.id = msg_count.conversation_id
    WHERE p.user_id = user_id_param
    GROUP BY p.id;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Comments for documentation
COMMENT ON TABLE profiles IS 'User profiles and preferences';
COMMENT ON TABLE conversations IS 'Conversation sessions between users and JarvisX';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE permissions IS 'User permission policies for different capabilities';
COMMENT ON TABLE skills IS 'Available skills and their metadata';
COMMENT ON TABLE skill_executions IS 'Log of skill executions and performance metrics';
COMMENT ON TABLE files IS 'File metadata and storage information';
COMMENT ON TABLE models IS 'Trained machine learning models';
COMMENT ON TABLE sessions IS 'User session management';
COMMENT ON TABLE audit_logs IS 'Security and activity audit trail';

COMMENT ON FUNCTION cleanup_expired_files() IS 'Removes expired temporary files';
COMMENT ON FUNCTION cleanup_expired_sessions() IS 'Removes expired user sessions';
COMMENT ON FUNCTION get_user_stats(TEXT) IS 'Returns comprehensive statistics for a user';