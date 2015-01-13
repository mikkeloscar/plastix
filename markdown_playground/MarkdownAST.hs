-- | An abstract syntax tree definition for the Fast language.
module MarkdownAST
       ( Level
       , Header (..)
       , Code (..)
       , Inline (..)
       , Block (..)
       , Document
       )
       where

-- | Level is an int
type Level = Int

data Header = Header { level :: Level
                     , inline :: Inline
                     }

data Code = Code { lang :: String
                 , code :: String }

data Inline = StringValue String
            | Space String
            | InlineCode String
            | Bold Inline
            | Italic Inline
            deriving (Eq, Show)

data Paragraph = Paragraph [Inline]

-- | Text block in plastix
data Block = Paragraph
           | Header
           | Blockquote
           | List
           | Code
           | Horizontal
           | Reference
           deriving (Eq, Show)

-- | A Document of blocks
type Document = [Block]
