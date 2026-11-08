CREATE TABLE session (
  id TEXT PRIMARY KEY,
  parent_id TEXT,
  directory TEXT NOT NULL,
  model TEXT,
  time_created INTEGER NOT NULL,
  time_updated INTEGER NOT NULL
);
CREATE TABLE message (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL,
  time_created INTEGER NOT NULL,
  time_updated INTEGER NOT NULL,
  data TEXT NOT NULL
);
CREATE TABLE part (
  id TEXT PRIMARY KEY,
  message_id TEXT NOT NULL,
  session_id TEXT NOT NULL,
  time_created INTEGER NOT NULL,
  time_updated INTEGER NOT NULL,
  data TEXT NOT NULL
);
INSERT INTO session VALUES ('ses_main', NULL, '/tmp/demo', 'kimi-k3.1-pro', 1000, 5000);
INSERT INTO session VALUES ('ses_sub', 'ses_main', '/tmp/demo', 'kimi-k3.1-pro', 2500, 3500);
INSERT INTO message VALUES ('msg_1', 'ses_main', 1100, 1100, '{"role":"assistant","modelID":"kimi-k3.1-pro","providerID":"zs","tokens":{"input":10,"output":5,"reasoning":1,"cache":{"read":2,"write":0}}}');
INSERT INTO part VALUES ('prt_1', 'msg_1', 'ses_main', 1200, 1200, '{"type":"tool","tool":"bash","state":{"status":"completed","output":"LITMUS-RUN-oc0001\nLITMUS-TASK-bug-py-01"}}');
INSERT INTO message VALUES ('msg_2', 'ses_main', 2000, 2000, '{"role":"assistant","modelID":"kimi-k3.1-pro","providerID":"zs","tokens":{"input":40,"output":15,"reasoning":3,"cache":{"read":20,"write":4}}}');
INSERT INTO message VALUES ('msg_3', 'ses_sub', 2600, 2600, '{"role":"assistant","modelID":"kimi-k3.1-pro","providerID":"zs","tokens":{"input":8,"output":4,"reasoning":0,"cache":{"read":0,"write":0}}}');
INSERT INTO part VALUES ('prt_2', 'msg_2', 'ses_main', 3000, 3000, '{"type":"tool","tool":"bash","state":{"status":"completed","output":"LITMUS-TASK-review-py-01"}}');
INSERT INTO message VALUES ('msg_4', 'ses_main', 4000, 4000, '{"role":"assistant","modelID":"qwen3.8-max","providerID":"zs","tokens":{"input":60,"output":25,"reasoning":6,"cache":{"read":30,"write":0}}}');
INSERT INTO part VALUES ('prt_bad', 'msg_4', 'ses_main', 4100, 4100, '{invalid-json');
