PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  role TEXT NOT NULL CHECK (role IN ('admin', 'evaluator', 'moderator')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS script_bundles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT NOT NULL,
  exam_code TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'assigned' CHECK (status IN ('assigned', 'in_progress', 'submitted', 'moderation', 'closed')),
  assigned_to INTEGER REFERENCES users(id),
  due_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS answer_scripts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bundle_id INTEGER NOT NULL REFERENCES script_bundles(id) ON DELETE CASCADE,
  masked_roll_no TEXT NOT NULL UNIQUE,
  page_count INTEGER NOT NULL CHECK (page_count > 0),
  status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'checking', 'draft_saved', 'submitted', 'flagged', 'moderated')),
  current_question INTEGER NOT NULL DEFAULT 1,
  total_awarded REAL NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS script_pages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  script_id INTEGER NOT NULL REFERENCES answer_scripts(id) ON DELETE CASCADE,
  page_number INTEGER NOT NULL,
  image_url TEXT NOT NULL,
  UNIQUE (script_id, page_number)
);

CREATE TABLE IF NOT EXISTS questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  subject TEXT NOT NULL,
  question_no TEXT NOT NULL,
  max_marks REAL NOT NULL CHECK (max_marks >= 0),
  rubric TEXT NOT NULL,
  UNIQUE (subject, question_no)
);

CREATE TABLE IF NOT EXISTS evaluations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  script_id INTEGER NOT NULL REFERENCES answer_scripts(id) ON DELETE CASCADE,
  evaluator_id INTEGER NOT NULL REFERENCES users(id),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'returned', 'approved')),
  remarks TEXT NOT NULL DEFAULT '',
  submitted_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (script_id, evaluator_id)
);

CREATE TABLE IF NOT EXISTS marks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  evaluation_id INTEGER NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
  question_id INTEGER NOT NULL REFERENCES questions(id),
  awarded_marks REAL NOT NULL CHECK (awarded_marks >= 0),
  comment TEXT NOT NULL DEFAULT '',
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (evaluation_id, question_id)
);

CREATE TABLE IF NOT EXISTS annotations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  evaluation_id INTEGER NOT NULL REFERENCES evaluations(id) ON DELETE CASCADE,
  page_id INTEGER NOT NULL REFERENCES script_pages(id),
  annotation_type TEXT NOT NULL CHECK (annotation_type IN ('tick', 'cross', 'note', 'highlight')),
  x REAL NOT NULL CHECK (x >= 0),
  y REAL NOT NULL CHECK (y >= 0),
  note TEXT NOT NULL DEFAULT '',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  actor_id INTEGER REFERENCES users(id),
  entity_type TEXT NOT NULL,
  entity_id INTEGER NOT NULL,
  action TEXT NOT NULL,
  details TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_answer_scripts_status ON answer_scripts(status);
CREATE INDEX IF NOT EXISTS idx_evaluations_script ON evaluations(script_id);
CREATE INDEX IF NOT EXISTS idx_marks_evaluation ON marks(evaluation_id);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
