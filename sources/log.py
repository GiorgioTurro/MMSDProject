class Log:
    log = open('../resources/log/log.txt', 'w')
    day_full_log = open('../resources/log/dayfulllog.txt', 'w')
    capacity_full_log = open('../resources/log/capacityfulllog.txt', 'w')

    def write_log(self, file, text):
        if file == 'log':
            self.log.write(text + '\n')
        elif file == 'day_full_log':
            self.day_full_log.write(text + '\n')
            self.log.write(text + '\n')
        elif file == 'capacity_full_log':
            self.capacity_full_log.write(text + '\n')
            self.log.write(text + '\n')

    def close(self):
        self.log.close()
        self.day_full_log.close()
        self.capacity_full_log.close()
