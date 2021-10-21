// Promise Queue, adapted from code by markosyan
// ensure that each added Promise is executed only after the other resolved
class Queue {
    static queue = [];
    static pendingPromise = false;
    static stop = false;
  
    static enqueue(promise) {
      return new Promise((resolve, reject) => {
          this.queue.push({
              promise,
              resolve,
              reject,
          });
          this.dequeue();
      });
    }
  
    static dequeue() {
      if (this.workingOnPromise) {
        return false;
      }
      if (this.stop) {
        this.queue = [];
        this.stop = false;
        return;
      }
      const item = this.queue.shift();
      if (!item) {
        return false;
      }
      try {
        this.workingOnPromise = true;
        item.promise()
          .then((value) => {
            this.workingOnPromise = false;
            item.resolve(value);
            this.dequeue();
          })
          .catch(err => {
            this.workingOnPromise = false;
            item.reject(err);
            this.dequeue();
          })
      } catch (err) {
        this.workingOnPromise = false;
        item.reject(err);
        this.dequeue();
      }
      return true;
    }
}