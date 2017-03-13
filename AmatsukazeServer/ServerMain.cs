﻿using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace AmatsukazeServer
{
    public static class ServerMain
    {
        private static int mainThreadId;
        private static SingleThreadSynchronizationContext syncCtx;

        public static void Start(string[] args)
        {
            mainThreadId = Thread.CurrentThread.ManagedThreadId;
            syncCtx = new SingleThreadSynchronizationContext();
            SynchronizationContext.SetSynchronizationContext(syncCtx);

            EncodeServer server = new EncodeServer();
            UserClient client = new UserClient();
            Task.WhenAll(
                server.ServerTask,
                client.CommTask,
                StartTest(server, client)
                ).ContinueWith(t => {
                FinishMain();
            });
            syncCtx.RunOnCurrentThread();

            Console.WriteLine("Finished");
        }

        private static async Task StartTest(EncodeServer server, UserClient client)
        {
            await Task.Delay(1000);

            Debug.Print("Server.RequestQueue");
            await client.Server.RequestQueue();
            Debug.Print("Server.RequestLog");
            await client.Server.RequestLog();
            Debug.Print("Server.RequestConsole");
            await client.Server.RequestConsole();
            Debug.Print("Server.RequestState");
            await client.Server.RequestState();

            await Task.Delay(1000);

            client.Finish();
            server.Finish();
        }

        public static void CheckThread()
        {
            if (Thread.CurrentThread.ManagedThreadId != mainThreadId)
            {
                Console.WriteLine(
                    "Error: ThreadId=" + Thread.CurrentThread.ManagedThreadId +
                    ", MainThreadId=" + mainThreadId);
            }
        }

        public static void FinishMain()
        {
            syncCtx.Complete();
        }

        private sealed class SingleThreadSynchronizationContext :
            SynchronizationContext
        {
            private readonly
                BlockingCollection<KeyValuePair<SendOrPostCallback, object>>
                m_queue =
                new BlockingCollection<KeyValuePair<SendOrPostCallback, object>>();

            public override void Post(SendOrPostCallback d, object state)
            {
                m_queue.Add(
                    new KeyValuePair<SendOrPostCallback, object>(d, state));
            }

            public void RunOnCurrentThread()
            {
                KeyValuePair<SendOrPostCallback, object> workItem;
                while (m_queue.TryTake(out workItem, Timeout.Infinite))
                    workItem.Key(workItem.Value);
            }

            public void Complete() { m_queue.CompleteAdding(); }
        }
    }

    public class Debug
    {
        [Conditional("DEBUG")]
        public static void Print(string str)
        {
            Console.WriteLine(str);
        }
    }
}
