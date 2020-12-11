// SPDX-License-Identifier: GPL-2.0-or-later
/*
 * net/sched/sch_fifo.c	The simplest FIFO queue.
 *
 * Authors:	Alexey Kuznetsov, <kuznet@ms2.inr.ac.ru>
 */

#include <linux/module.h>
#include <linux/slab.h>
#include <linux/types.h>
#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/skbuff.h>
#include <net/pkt_sched.h>
#include <net/pkt_cls.h>

static int sample_enqueue(struct sk_buff *skb, struct Qdisc *sch,
			 struct sk_buff **to_free)
{
	if (likely(sch->q.qlen < sch->limit))
		return qdisc_enqueue_tail(skb, sch);

	return qdisc_drop(skb, sch, to_free);
}

static int sample_init(struct Qdisc *sch, struct nlattr *opt,
		       struct netlink_ext_ack *extack)
{
	sch->limit = qdisc_dev(sch)->tx_queue_len;

	if (sch->limit >= 1)
		sch->flags |= TCQ_F_CAN_BYPASS;
	else
		sch->flags &= ~TCQ_F_CAN_BYPASS;

	return 0;
}

static int sample_dump(struct Qdisc *sch, struct sk_buff *skb)
{
	struct tc_fifo_qopt opt = { .limit = sch->limit };

	if (nla_put(skb, TCA_OPTIONS, sizeof(opt), &opt))
		goto nla_put_failure;
	return skb->len;

nla_put_failure:
	return -1;
}


struct Qdisc_ops sample_qdisc_ops __read_mostly = {
	.id		=	"sample",
	.priv_size	=	0,
	.enqueue	=	sample_enqueue,
	.dequeue	=	qdisc_dequeue_head,
	.peek		=	qdisc_peek_head,
	.init		=	sample_init,
	.reset		=	qdisc_reset_queue,
	.change		=	sample_init,
	.dump		=	sample_dump,
	.owner		=	THIS_MODULE,
};
EXPORT_SYMBOL(sample_qdisc_ops);

MODULE_LICENSE("GPL");
