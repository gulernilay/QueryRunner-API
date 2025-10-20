SELECT TOP (1000) [key_]
      ,[prompt]
      ,[query]
  FROM [ChefPanel_test].[dbo].[nly_sql_api]


UPDATE dbo.nly_sql_api 
SET query = 'SELECT ((SELECT SUM(Loc_Debit-Loc_Credit) FROM AllJournals WITH(NOLOCK) WHERE JournalDate=''20250102'' AND SUBSTRING(GLAccCode,1,3) IN (''120'',''126'',''127'',''128'',''129'')) + (SELECT SUM(Loc_Debit-Loc_Credit) FROM AllJournals WITH(NOLOCK) WHERE JournalDate BETWEEN ''20250102'' AND ''20250831'' AND SUBSTRING(GLAccCode,1,3) IN (''120'',''126'',''127'',''128'',''129'')) )/2 AS OrtalamaTicariAlacaklar;' 
WHERE key_ = 'Ortalama_Ticari_Alacaklar'




