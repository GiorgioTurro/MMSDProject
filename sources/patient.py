def patient(env, log, name, gg_al_ricovero, gg_degenza, resource, optional_year_resource):
    yield env.timeout(gg_al_ricovero)
    with resource.request() as req:
        resource_request_time = env.now
        yield req
        if optional_year_resource is not None:
            req2 = optional_year_resource.request()
            yield req2
        resource_provided_time = env.now
        if resource_provided_time - resource_request_time != 0:
            log.write_log('capacity_full_log', "Patient: " + str(name) +
                          " Request resource at: " + str(resource_request_time) +
                          " But received it at: " + str(resource_provided_time))
        log.write_log('log', ('Start hospitalization of: %d at %d' % (name, env.now)))
        yield env.timeout(gg_degenza)
        if optional_year_resource is not None:
            optional_year_resource.release(req2)
        log.write_log('log', ('End hospitalization of: %d at %d' % (name, env.now)))
