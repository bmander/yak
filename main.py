from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
import os
import sys

Base = declarative_base()

class Task(Base):
  __tablename__ = 'tasks'
  
  id = Column( Integer, primary_key=True )
  description = Column( Text )
  created = Column( DateTime )
  started = Column( DateTime )
  finished = Column( DateTime )
  parent_id = Column( Integer, ForeignKey('tasks.id') )

  parent = relationship("Task", backref='children', remote_side="Task.id")

  def __init__( self, description, parent=None, start=False ):
    self.description = description
    self.created = datetime.now()
    self.parent = parent
    if start:
      self.started = self.created
    
  def start( self, start_time=None ):
    self.started = start_time if start_time else datetime.now()

  def finish( self, finish_time=None ):
    self.finished = finish_time if finish_time else datetime.now()

  def __repr__(self):
    return "%s %s"%(self.id, self.description)

class Status(Base):
  __tablename__ = "status"

  id = Column( Integer, primary_key=True )
  current_task_id = Column( Integer, ForeignKey( 'tasks.id' ) )

  current_task = relationship( "Task" )

  def __init__(self):
    self.task = None

class Stack(object):
  def __init__(self, session):
    self.session = session

  def current_status( self ):
    status = self.session.query( Status ).first()

    if status is None:
      status = Status()
      session.add( status )

    return status

  def current_task( self ):
    return self.current_status().current_task

  def new(self, description):
    task = Task( description=description )
    self.session.add( task )

  def push(self, description):
    status = self.current_status()

    task = Task( description=description, parent=status.current_task, start=True )
    self.session.add( task )

    status.current_task = task

  def pop(self):
    status = self.current_status()

    if status.current_task is None:
      return

    status.current_task.finished = datetime.now()
    status.current_task = status.current_task.parent

  def list(self):
    for task in self.session.query(Task).filter(Task.finished != None):
      print task

  def switch(self, id):
    next_task = self.session.query(Task).get(id)
    if next_task is None:
      print "There is no task with an id %s"%id
      return

    self.current_status().current_task = next_task

if __name__=='__main__':

  metadata = Base.metadata

  # start database
  yakstack_path = os.path.expanduser("~/.yakstack")
  engine = create_engine('sqlite:///'+yakstack_path, echo=False)

  # flesh out database
  metadata.create_all( engine )

  # get a session 
  Session = sessionmaker(bind=engine)
  session = Session()

  stack = Stack( session )

  print sys.argv

  if len(sys.argv)<2:
    print "usage: yak new|push|pop|list|switch"
    exit()

  command = sys.argv[1]

  if command=="new":
    if len(sys.argv<3):
      print "usage: yak new task_description"
      exit()

    stack.new( " ".join( sys.argv[2:] ) )

  #stack.push( "this is a thing yeah yeah" )

  #stack.pop( )

  #stack.list( )

  #stack.switch( 12 )

  #print stack.current_task()

  session.commit()
