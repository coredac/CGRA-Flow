"""
==========================================================================
Branch_test.py
==========================================================================
Test cases for functional unit branch.

Author : Cheng Tan
  Date : November 27, 2019

"""

from pymtl3 import *
from pymtl3.stdlib.test           import TestSinkCL
from pymtl3.stdlib.test.test_srcs import TestSrcRTL

from ..Branch                     import Branch
from ....lib.opt_type             import *
from ....lib.messages             import *

#-------------------------------------------------------------------------
# Test harness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, FunctionUnit, DataType, CtrlType,
                 src_data, src_comp, src_opt, sink_if, sink_else ):

    s.src_data  = TestSrcRTL( DataType, src_data  )
    s.src_comp  = TestSrcRTL( DataType, src_comp  )
    s.src_opt   = TestSrcRTL( CtrlType, src_opt   )
    s.sink_if   = TestSinkCL( DataType, sink_if   )
    s.sink_else = TestSinkCL( DataType, sink_else )

    s.dut = FunctionUnit( DataType, CtrlType )

    connect( s.src_data.send, s.dut.recv_in0   )
    connect( s.src_comp.send, s.dut.recv_in1   )
    connect( s.src_opt.send,  s.dut.recv_opt   )
    connect( s.dut.send_out0, s.sink_if.recv   )
    connect( s.dut.send_out1, s.sink_else.recv )

  def done( s ):
    return s.src_data.done() and s.src_comp.done()  and s.src_opt.done() and\
           s.sink_if.done()  and s.sink_else.done() 

  def line_trace( s ):
    return s.dut.line_trace()

def run_sim( test_harness, max_cycles=100 ):
  test_harness.elaborate()
  test_harness.apply( SimulationPass() )
  test_harness.sim_reset()

  # Run simulation

  ncycles = 0
  print()
  print( "{}:{}".format( ncycles, test_harness.line_trace() ))
  while not test_harness.done() and ncycles < max_cycles:
    test_harness.tick()
    ncycles += 1
    print( "{}:{}".format( ncycles, test_harness.line_trace() ))

  # Check timeout

  assert ncycles < max_cycles

  test_harness.tick()
  test_harness.tick()
  test_harness.tick()

def test_Branch():
  FU = Branch
  DataType  = mk_data( 16, 1 )
  CtrlType  = mk_ctrl()
  src_data  = [ DataType(7, 1), DataType(3, 1), DataType(9, 1) ]
  src_comp  = [ DataType(0, 1), DataType(1, 1), DataType(0, 1) ]
  src_opt   = [ CtrlType( OPT_BRH ),
                CtrlType( OPT_BRH ),
                CtrlType( OPT_BRH ) ]
  sink_if   = [ DataType(7, 1), DataType(3, 0), DataType(9, 1) ]
  sink_else = [ DataType(7, 0), DataType(3, 1), DataType(9, 0) ]
  th = TestHarness( FU, DataType, CtrlType, src_data, src_comp, src_opt,
                    sink_if, sink_else )

  run_sim( th )
