CREATE TABLE FDE_VIEWS.AgentAuditLog (
    LogID        INT            IDENTITY (1, 1) PRIMARY KEY,
    Timestamp    DATETIME       DEFAULT GETDATE(),
    SessionID    VARCHAR (50)  ,
    NodeExecuted VARCHAR (50)  ,
    ToolName     VARCHAR (100) ,
    Content      NVARCHAR (MAX) -- NVARCHAR to safely handle JSON strings and large LLM outputs );
);

-- otherwise we cannoy insrt into it
GRANT INSERT
    ON FDE_VIEWS.AgentAuditLog TO USR_FDE_RO;