```mermaid 
erDiagram
    CONTENTMETADATA {
        meta_id  UUID PK
        title String
        description String
        author String
        abstract String
        keywords list[String]
        date_published DateTime
        citation Optional[String]  
        }
        CONTENTRECORD{
            content_id UUID PK
            original_content String
            content_type String
            title String
            summary String
            category String
            tags list[String]
            embedding  list[Float]
            timestamp DateTime
            source_url Optional[String]
            meta_data  CONTENTMETADATA FK
        }
    CONTENTRECORD ||--o{  CONTENTMETADATA : contains
    
    QUIZQUESTION {
        Quiz_num int PK
        topcic String
        question String
        explanation String
        choices list[String]
    }
    QUIZ{
        title String
        quiz_id UUID PK
        questions list[QUIZQUESTION]
    }
    QUIZRESULT {
        quiz_id UUID PK
        user_id UUID FK
        score int
    }
    QUIZRESULT {
        quiz_id UUID PK
        user_id UUID FK
        score int
        total float
    }
    QUIZ ||--o{ QUIZQUESTION : contains
    QUIZRESULT ||--o{ QUIZ : takes

    TOOLRESPONSE{
        status String
        data Optional[ANY]
        message Optional[String]
    }
    ERRORRESPONSE{
        status String
        details Optional[ANY]
    }
    SUCCESSRESPONSE{
        results Optional[String]
        data Optional[ANY]
    }