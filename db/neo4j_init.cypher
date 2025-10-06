// ============================
// Sample Nodes
// ============================
CREATE (:Student {id:'S1001', name:'Alice Sharma', email:'alice@campus.edu'});
CREATE (:Student {id:'S1002', name:'Bob Kumar', email:'bob@campus.edu'});
CREATE (:Staff {id:'T2001', name:'Dr. Neha', email:'neha@campus.edu'});
CREATE (:Card {id:'C1001'});
CREATE (:Card {id:'C1002'});
CREATE (:Card {id:'C2001'});
CREATE (:Device {hash:'D1001'});
CREATE (:Device {hash:'D1002'});
CREATE (:Device {hash:'D1003'});
CREATE (:Location {id:'Library'});
CREATE (:Location {id:'MainGate'});
CREATE (:Room {id:'Lab101'});

// ============================
// Relationships
// ============================
MATCH (s:Student {id:'S1001'}), (c:Card {id:'C1001'}) CREATE (s)-[:HAS_CARD]->(c);
MATCH (s:Student {id:'S1002'}), (c:Card {id:'C1002'}) CREATE (s)-[:HAS_CARD]->(c);
MATCH (t:Staff {id:'T2001'}), (c:Card {id:'C2001'}) CREATE (t)-[:HAS_CARD]->(c);

MATCH (s:Student {id:'S1001'}), (d:Device {hash:'D1001'}) CREATE (s)-[:USES_DEVICE]->(d);
MATCH (s:Student {id:'S1002'}), (d:Device {hash:'D1002'}) CREATE (s)-[:USES_DEVICE]->(d);
MATCH (t:Staff {id:'T2001'}), (d:Device {hash:'D1003'}) CREATE (t)-[:USES_DEVICE]->(d);

MATCH (c:Card {id:'C1001'}), (l:Location {id:'MainGate'}) CREATE (c)-[:SWIPED_AT {timestamp: datetime()}]->(l);
MATCH (c:Card {id:'C1002'}), (l:Location {id:'Library'}) CREATE (c)-[:SWIPED_AT {timestamp: datetime()}]->(l);

MATCH (s:Student {id:'S1001'}), (r:Room {id:'Lab101'}) CREATE (s)-[:BOOKED {start: datetime(), end: datetime()}]->(r);
