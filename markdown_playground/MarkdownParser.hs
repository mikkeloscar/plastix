module MarkdownParser
( Error
, parseString
, parseFile
-- exported to make testing easier
, expr
, consDecl
, classDecl
, recvDecl
) where

import SimpleParse -- from Ken's github repo. Commit: 845543f83c9b1c6a24f0e2c7dc45a48aa10f131b
import MarkdownAST -- AST
import Data.Char (isDigit, isAlpha, ord) -- import Char functions

-- Use applicative functions like <$>, <|> and some
import Control.Applicative ((<$>), (<|>), some)

-- Use Data.Set to store keywords
import qualified Data.Set as Set

type Keywords = Set.Set String

-- | You may change this type to whatever you want - just make sure it
-- is an instance of 'Show'.
data Error = ParseError deriving (Show, Read, Eq)

-- digit and integer is based on code from `sep18.hs` from absalon (30/10/2014)
digit :: Parser Integer
digit = num <$> satisfy isDigit
  where num c = toInteger $ ord c - ord '0'

-- Parse IntValue
integer :: Parser Integer
integer = token $ foldl (\acc d -> acc * 10 + d) 0 <$> some digit

notQuote :: Char -> Bool
notQuote s = s /= '"'

-- Parse StringValue
str :: Parser String
str = token $ do _ <- string "\""
                 s <- munch notQuote
                 _ <- string "\""
                 return s

-- Set of keywords in the Fast language
-- (compared to lists this gives us O(log n) lookup vs. O(n))
keywords :: Keywords
keywords = Set.fromAscList ["class", "match", "new", "receive", "return",
                            "self", "send", "set"]

-- based on constituent function from sep18.hs from absalon (20/9/2014)
constituent :: Char -> Bool
constituent c = isAlpha c || c == '_' || isDigit c

name :: Parser Name
name = token $ do n <- satisfy isAlpha -- a Name has to start with an alpha char
                  s <- munch constituent
                  if Set.member (n:s) keywords
                  then reject
                  else return (n:s)

-- from sep18.hs from Absalon (20/9/2014)
keyword :: String -> Parser ()
keyword s = do _ <- symbol s
               notFollowedBy $ satisfy constituent


header :: Parser Header
header = do l <- munch1 (\s -> s == '#')
            _ <- munch space
            i <- inline

-- Args
args :: Parser [Expr]
args = do e <- expr
          _ <- symbol ","
          as <- args
          return (e:as)
       <|> do e <- expr
              return [e]
       <|> return []

-- Exprs
exprs :: Parser Exprs
exprs = do e <- expr
           _ <- symbol ";"
           es <- exprs
           return (e:es)
        <|> return []

-- Params
params :: Parser [Name]
params = do n <- name
            _ <- symbol ","
            ps <- params
            return (n:ps)
         <|> do n <- name
                return [n]
         <|> return []

-- Helper function to parse the construct: "Name '(' Args ')'"
nameArgs :: Parser (Name, [Expr])
nameArgs = do n <- name
              _ <- symbol "("
              as <- args
              _ <- symbol ")"
              return (n, as)

-- Expr
intConst :: Parser Expr
intConst = do i <- integer
              return $ IntConst i

stringConst :: Parser Expr
stringConst = do s <- str
                 return $ StringConst s

term :: Parser Expr
term = do (n, as) <- nameArgs
          return $ TermLiteral n as

self :: Parser Expr
self = do keyword "self"
          return Self

plus :: Parser (Expr -> Expr -> Expr)
plus = do _ <- symbol "+"
          return Plus

minus :: Parser (Expr -> Expr -> Expr)
minus = do _ <- symbol "-"
           return Minus

times :: Parser (Expr -> Expr -> Expr)
times = do _ <- symbol "*"
           return Times

dividedBy :: Parser (Expr -> Expr -> Expr)
dividedBy = do _ <- symbol "/"
               return DividedBy

-- return
rturn :: Parser Expr
rturn = do keyword "return"
           e <- expr
           return $ Return e

field :: Parser Name
field = do keyword "self"
           _ <- symbol "."
           name

setField :: Parser Expr
setField = do keyword "set"
              n <- field
              _ <- symbol "="
              e <- expr
              return $ SetField n e

setVar :: Parser Expr
setVar = do keyword "set"
            n <- name
            _ <- symbol "="
            e <- expr
            return $ SetVar n e

readVar :: Parser Expr
readVar = do n <- name
             return $ ReadVar n

readField :: Parser Expr
readField = do n <- field
               return $ ReadField n

match :: Parser Expr
match = do keyword "match"
           e <- expr
           _ <- symbol "{"
           c <- cases
           _ <- symbol "}"
           return $ Match e c

sendMessage :: Parser Expr
sendMessage = do keyword "send"
                 _ <- symbol "("
                 e1 <- expr
                 _ <- symbol ","
                 e2 <- expr
                 _ <- symbol ")"
                 return $ SendMessage e1 e2

-- callMethod handles the contruct: expr '.' Name '(' args ')'
-- I have been unable to prevent an infinite loop when parsing this construct,
-- so I have used an abritary limit for the number of chained method calls
-- allowed in the language. Documented further in the report.
callMethod :: Parser Expr -> Int -> Parser Expr
callMethod x i = if i > 2 -- abritary method chaining limit, higher limit = slower parsing
                 then x
                 else do e <- callMethod x (i+1)
                         _ <- symbol "."
                         (n, as) <- nameArgs
                         return $ CallMethod e n as
                      <|> x

new :: Parser Expr
new = do keyword "new"
         (n, as) <- nameArgs
         return $ New n as

expr :: Parser Expr
expr = chainl1 expr1 op1
    where op1 = plus <|> minus
          expr1 = chainl1 expr0 op2
          op2 = times <|> dividedBy

expr0 :: Parser Expr
expr0 = callMethod expr1 0
    where expr1 = intConst
                  <|> stringConst
                  <|> term
                  <|> self
                  <|> rturn
                  <|> setField
                  <|> setVar
                  <|> readVar
                  <|> readField
                  <|> match
                  <|> sendMessage
                  <|> new
                  <|> do _ <- symbol "("
                         e <- expr
                         _ <- symbol ")"
                         return e

-- Case
case_ :: Parser Case
case_ = do p <- pattern
           _ <- symbol "->"
           es <- exprsExp
           return (p, es)

cases :: Parser Cases
cases = do c <- case_
           cs <- cases
           return (c:cs)
        <|> return []

-- Pattern
constInt :: Parser Pattern
constInt = do i <- integer
              return $ ConstInt i

constString :: Parser Pattern
constString = do s <- str
                 return $ ConstString s

termPattern :: Parser Pattern
termPattern = do n <- name
                 ps <- paramExp
                 return $ TermPattern n ps

anyValue :: Parser Pattern
anyValue = do n <- name
              return $ AnyValue n

pattern :: Parser Pattern
pattern = constInt
        <|> constString
        <|> termPattern
        <|> anyValue

-- RecvDecl
recvDecl :: Parser (Maybe ReceiveDecl)
recvDecl = do keyword "receive"
              _ <- symbol "("
              p <- name
              _ <- symbol ")"
              es <- exprsExp
              return $ Just ReceiveDecl {receiveParam = p, receiveBody = es}
           <|> return Nothing

paramExp :: Parser [Name]
paramExp = do _ <- symbol "("
              ps <- params
              _ <- symbol ")"
              return ps

exprsExp :: Parser Exprs
exprsExp = do _ <- symbol "{"
              es <- exprs
              _ <- symbol "}"
              return es

paramsExprs :: Parser ([Name], Exprs)
paramsExprs = do ps <- paramExp
                 es <- exprsExp
                 return (ps, es)

-- NamedMethodDecl
namedMethodDecl :: Parser NamedMethodDecl
namedMethodDecl = do n <- name
                     (ps, es) <- paramsExprs
                     return $ NamedMethodDecl n MethodDecl {methodParameters = ps,
                                                            methodBody = es}

namedMethodDecls :: Parser [NamedMethodDecl]
namedMethodDecls = do n <- namedMethodDecl
                      ns <- namedMethodDecls
                      return (n:ns)
                   <|> return []

-- ConstructorDecl
consDecl :: Parser (Maybe ConstructorDecl)
consDecl = do keyword "new"
              (ps, es) <- paramsExprs
              return $ Just MethodDecl {methodParameters = ps, methodBody = es}
           <|> return Nothing

-- ClassDecl
classDecl :: Parser ClassDecl
classDecl = do keyword "class"
               n <- name
               _ <- symbol "{"
               cons <- consDecl
               methods <- namedMethodDecls
               recv <- recvDecl
               _ <- symbol "}"
               return ClassDecl {className = n,
                                 classConstructor = cons,
                                 classMethods = methods,
                                 classReceive = recv}

classDecls :: Parser [ClassDecl]
classDecls = do c <- classDecl
                cs <- classDecls
                return (c:cs)
             <|> return []

-- Program
program :: Parser Prog
program = classDecls

parseString :: String -> Either Error Prog
parseString s = case prog of
                    []  -> Left ParseError
                    p:_ -> Right p
    where prog = parse' (do s' <- program
                            token eof
                            return s') s

parseFile :: FilePath -> IO (Either Error Prog)
parseFile filename = parseString <$> readFile filename
