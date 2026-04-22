from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class TimeoutController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

        log.info("Switch connected")

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        in_port = event.port

        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, in_port)

        msg.idle_timeout = 10
        msg.hard_timeout = 0
        msg.priority = 10

        msg.actions.append(
            of.ofp_action_output(port=of.OFPP_FLOOD)
        )

        msg.data = event.ofp
        self.connection.send(msg)

        log.info("Flow installed with idle timeout")

def launch():
    def start_switch(event):
        log.info("Controlling switch")
        TimeoutController(event.connection)

    core.openflow.addListenerByName(
        "ConnectionUp",
        start_switch
    )
